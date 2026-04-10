import os
import hashlib
from datetime import datetime
from contextlib import contextmanager

# Intentar importar psycopg2, si no está, usar SQLite
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# Configuración de base de datos
DATABASE_URL = os.getenv('DATABASE_URL')


def get_db_connection():
    """Retorna conexión a Supabase (PostgreSQL) o SQLite"""
    if DATABASE_URL and PSYCOPG2_AVAILABLE:
        # Producción: Supabase (PostgreSQL)
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    else:
        # Desarrollo local: SQLite
        import sqlite3
        os.makedirs('data', exist_ok=True)
        return sqlite3.connect('data/users.db')


@contextmanager
def get_db_cursor(commit=False):
    """Context manager para manejar conexiones y cursores"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    finally:
        conn.commit()
        cursor.close()
        conn.close()


def hash_password(password: str) -> str:
    """Hashea una contraseña con SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """Inicializa las tablas en Supabase o SQLite"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Determinar si estamos en PostgreSQL o SQLite
    is_postgres = DATABASE_URL and PSYCOPG2_AVAILABLE
    
    if is_postgres:
        # PostgreSQL syntax
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                company_name TEXT,
                plan TEXT DEFAULT 'basic',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                fb_app_id TEXT,
                fb_access_token TEXT,
                fb_account_id TEXT
            )
        ''')
    else:
        # SQLite syntax
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                company_name TEXT,
                plan TEXT DEFAULT 'basic',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                fb_app_id TEXT,
                fb_access_token TEXT,
                fb_account_id TEXT
            )
        ''')
    
    # Crear admin por defecto si no existe
    admin_password_hash = hash_password("admin123")
    
    if is_postgres:
        cursor.execute("SELECT * FROM admin WHERE email = %s", ("admin@adsintelligence.com",))
    else:
        cursor.execute("SELECT * FROM admin WHERE email = ?", ("admin@adsintelligence.com",))
    
    if not cursor.fetchone():
        if is_postgres:
            cursor.execute(
                "INSERT INTO admin (email, password_hash) VALUES (%s, %s)",
                ("admin@adsintelligence.com", admin_password_hash)
            )
        else:
            cursor.execute(
                "INSERT INTO admin (email, password_hash) VALUES (?, ?)",
                ("admin@adsintelligence.com", admin_password_hash)
            )
    
    conn.commit()
    conn.close()


def verify_user(email: str, password: str) -> dict | None:
    """Verifica credenciales de un cliente"""
    is_postgres = DATABASE_URL and PSYCOPG2_AVAILABLE
    conn = get_db_connection()
    
    try:
        if is_postgres:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE email = %s AND is_active = 1", (email,))
        else:
            conn.row_factory = lambda c, row: {col[0]: row[i] for i, col in enumerate(c.description)}
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
        
        user = cursor.fetchone()
        
        if user and user['password_hash'] == hash_password(password):
            if is_postgres:
                cursor.execute(
                    "UPDATE users SET last_login = %s WHERE id = %s",
                    (datetime.now(), user['id'])
                )
            else:
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now(), user['id'])
                )
            conn.commit()
            conn.close()
            return dict(user)
    except Exception as e:
        print(f"Error en verify_user: {e}")
    
    conn.close()
    return None


def verify_admin(email: str, password: str) -> dict | None:
    """Verifica credenciales de administrador"""
    is_postgres = DATABASE_URL and PSYCOPG2_AVAILABLE
    conn = get_db_connection()
    
    try:
        if is_postgres:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
        else:
            conn.row_factory = lambda c, row: {col[0]: row[i] for i, col in enumerate(c.description)}
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE email = ?", (email,))
        
        admin = cursor.fetchone()
        
        if admin and admin['password_hash'] == hash_password(password):
            conn.close()
            return dict(admin)
    except Exception as e:
        print(f"Error en verify_admin: {e}")
    
    conn.close()
    return None


def create_user(email: str, password: str, company_name: str, plan: str = 'basic') -> bool:
    """Crea un nuevo usuario cliente"""
    is_postgres = DATABASE_URL and PSYCOPG2_AVAILABLE
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if is_postgres:
            cursor.execute(
                "INSERT INTO users (email, password_hash, company_name, plan) VALUES (%s, %s, %s, %s)",
                (email, hash_password(password), company_name, plan)
            )
        else:
            cursor.execute(
                "INSERT INTO users (email, password_hash, company_name, plan) VALUES (?, ?, ?, ?)",
                (email, hash_password(password), company_name, plan)
            )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error en create_user: {e}")
        conn.close()
        return False


def update_user_credentials(user_id: int, fb_app_id: str, fb_access_token: str, fb_account_id: str):
    """Actualiza credenciales de Facebook de un cliente"""
    is_postgres = DATABASE_URL and PSYCOPG2_AVAILABLE
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if is_postgres:
            cursor.execute(
                "UPDATE users SET fb_app_id = %s, fb_access_token = %s, fb_account_id = %s WHERE id = %s",
                (fb_app_id, fb_access_token, fb_account_id, user_id)
            )
        else:
            cursor.execute(
                "UPDATE users SET fb_app_id = ?, fb_access_token = ?, fb_account_id = ? WHERE id = ?",
                (fb_app_id, fb_access_token, fb_account_id, user_id)
            )
        conn.commit()
    except Exception as e:
        print(f"Error en update_user_credentials: {e}")
    
    conn.close()


def get_user_credentials(user_id: int) -> dict:
    """Obtiene credenciales de Facebook de un cliente"""
    is_postgres = DATABASE_URL and PSYCOPG2_AVAILABLE
    conn = get_db_connection()
    
    try:
        if is_postgres:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT fb_app_id, fb_access_token, fb_account_id FROM users WHERE id = %s",
                (user_id,)
            )
        else:
            conn.row_factory = lambda c, row: {col[0]: row[i] for i, col in enumerate(c.description)}
            cursor = conn.cursor()
            cursor.execute(
                "SELECT fb_app_id, fb_access_token, fb_account_id FROM users WHERE id = ?",
                (user_id,)
            )
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'fb_app_id': user['fb_app_id'] or '',
                'fb_access_token': user['fb_access_token'] or '',
                'fb_account_id': user['fb_account_id'] or ''
            }
    except Exception as e:
        print(f"Error en get_user_credentials: {e}")
    
    return {}


def save_user_credentials(user_id: int, fb_app_id: str, fb_token: str, fb_account: str):
    """Guarda credenciales (alias de update_user_credentials)"""
    update_user_credentials(user_id, fb_app_id, fb_token, fb_account)


def get_all_users() -> list:
    """Obtiene todos los usuarios clientes"""
    is_postgres = DATABASE_URL and PSYCOPG2_AVAILABLE
    conn = get_db_connection()
    
    try:
        if is_postgres:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT id, email, company_name, plan, is_active, created_at, last_login FROM users")
        else:
            conn.row_factory = lambda c, row: {col[0]: row[i] for i, col in enumerate(c.description)}
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, company_name, plan, is_active, created_at, last_login FROM users")
        
        users = cursor.fetchall()
        conn.close()
        return [dict(user) for user in users]
    except Exception as e:
        print(f"Error en get_all_users: {e}")
        conn.close()
        return []


def delete_user(user_id: int):
    """Elimina un usuario"""
    is_postgres = DATABASE_URL and PSYCOPG2_AVAILABLE
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if is_postgres:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    except Exception as e:
        print(f"Error en delete_user: {e}")
    
    conn.close()


def log_access(user_id: int, action: str, ip: str):
    """Registra un acceso en el log"""
    is_postgres = DATABASE_URL and PSYCOPG2_AVAILABLE
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if is_postgres:
            cursor.execute(
                "INSERT INTO access_logs (user_id, action, ip_address) VALUES (%s, %s, %s)",
                (user_id, action, ip)
            )
        else:
            cursor.execute(
                "INSERT INTO access_logs (user_id, action, ip_address) VALUES (?, ?, ?)",
                (user_id, action, ip)
            )
        conn.commit()
    except Exception as e:
        print(f"Error en log_access: {e}")
    
    conn.close()


def get_user_by_id(user_id: int) -> dict | None:
    """Obtiene un usuario por su ID"""
    is_postgres = DATABASE_URL and PSYCOPG2_AVAILABLE
    conn = get_db_connection()
    
    try:
        if is_postgres:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        else:
            conn.row_factory = lambda c, row: {col[0]: row[i] for i, col in enumerate(c.description)}
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        print(f"Error en get_user_by_id: {e}")
        conn.close()
        return None


def get_recent_logs(limit: int = 10) -> list:
    """Obtiene los últimos logs de acceso"""
    is_postgres = DATABASE_URL and PSYCOPG2_AVAILABLE
    conn = get_db_connection()
    
    try:
        if is_postgres:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT l.*, u.email 
                FROM access_logs l
                JOIN users u ON l.user_id = u.id
                ORDER BY l.timestamp DESC
                LIMIT %s
            """, (limit,))
        else:
            conn.row_factory = lambda c, row: {col[0]: row[i] for i, col in enumerate(c.description)}
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.*, u.email 
                FROM access_logs l
                JOIN users u ON l.user_id = u.id
                ORDER BY l.timestamp DESC
                LIMIT ?
            """, (limit,))
        
        logs = cursor.fetchall()
        conn.close()
        return [dict(log) for log in logs]
    except Exception as e:
        print(f"Error en get_recent_logs: {e}")
        conn.close()
        return []


def update_user_plan(user_id: int, new_plan: str):
    """Actualiza el plan de un usuario"""
    is_postgres = DATABASE_URL and PSYCOPG2_AVAILABLE
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if is_postgres:
            cursor.execute("UPDATE users SET plan = %s WHERE id = %s", (new_plan, user_id))
        else:
            cursor.execute("UPDATE users SET plan = ? WHERE id = ?", (new_plan, user_id))
        conn.commit()
    except Exception as e:
        print(f"Error en update_user_plan: {e}")
    
    conn.close()