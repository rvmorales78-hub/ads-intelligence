import importlib
import os
import hashlib
from datetime import datetime

# Intentar importar psycopg2 para PostgreSQL
psycopg2 = None
RealDictCursor = None
try:
    psycopg2 = importlib.import_module('psycopg2')
    psycopg2_extras = importlib.import_module('psycopg2.extras')
    RealDictCursor = getattr(psycopg2_extras, 'RealDictCursor', None)
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

DATABASE_URL = os.getenv('DATABASE_URL', '')
IS_POSTGRES = bool(DATABASE_URL and PSYCOPG2_AVAILABLE)


# ========== CONEXIÓN ==========

def get_db_connection():
    """Retorna conexión a PostgreSQL o SQLite según entorno"""
    if IS_POSTGRES:
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    else:
        import sqlite3
        db_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(os.path.join(db_dir, 'users.db'))
        conn.row_factory = sqlite3.Row
        return conn


def hash_password(password: str) -> str:
    """Hashea una contraseña con SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


# ========== INICIALIZACIÓN ==========

def init_db():
    """Inicializa las tablas según el motor de BD"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if IS_POSTGRES:
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                action TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Crear admin por defecto si no existe
    admin_password_hash = hash_password("admin123")
    
    if IS_POSTGRES:
        cursor.execute("SELECT * FROM admin WHERE email = %s", ("admin@adsintelligence.com",))
    else:
        cursor.execute("SELECT * FROM admin WHERE email = ?", ("admin@adsintelligence.com",))
    
    if not cursor.fetchone():
        if IS_POSTGRES:
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


# ========== VERIFICACIONES ==========

def verify_user(email: str, password: str) -> dict | None:
    """Verifica credenciales de un cliente"""
    conn = get_db_connection()
    
    if IS_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s AND is_active = 1", (email,))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
    
    user = cursor.fetchone()
    
    if user and user['password_hash'] == hash_password(password):
        if IS_POSTGRES:
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
    
    conn.close()
    return None


def verify_admin(email: str, password: str) -> dict | None:
    """Verifica credenciales de administrador"""
    conn = get_db_connection()
    
    if IS_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE email = ?", (email,))
    
    admin = cursor.fetchone()
    
    if admin and admin['password_hash'] == hash_password(password):
        conn.close()
        return dict(admin)
    
    conn.close()
    return None


# ========== CRUD USUARIOS ==========

def create_user(email: str, password: str, company_name: str, plan: str = 'basic') -> bool:
    """Crea un nuevo usuario cliente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if IS_POSTGRES:
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
    except Exception:
        conn.close()
        return False


def get_all_users() -> list:
    """Obtiene todos los usuarios clientes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if IS_POSTGRES:
        cursor.execute("SELECT id, email, company_name, plan, is_active, created_at, last_login FROM users")
    else:
        cursor.execute("SELECT id, email, company_name, plan, is_active, created_at, last_login FROM users")
    
    users = cursor.fetchall()
    conn.close()
    
    return [dict(user) for user in users]


def get_user_by_id(user_id: int) -> dict | None:
    """Obtiene un usuario por su ID"""
    conn = get_db_connection()
    
    if IS_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None


def delete_user(user_id: int):
    """Elimina un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if IS_POSTGRES:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    else:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def update_user_plan(user_id: int, new_plan: str):
    """Actualiza el plan de un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if IS_POSTGRES:
        cursor.execute("UPDATE users SET plan = %s WHERE id = %s", (new_plan, user_id))
    else:
        cursor.execute("UPDATE users SET plan = ? WHERE id = ?", (new_plan, user_id))
    conn.commit()
    conn.close()


# ========== CREDENCIALES FACEBOOK ==========

def update_user_credentials(user_id: int, fb_app_id: str, fb_access_token: str, fb_account_id: str):
    """Actualiza credenciales de Facebook de un cliente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if IS_POSTGRES:
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
    conn.close()


def get_user_credentials(user_id: int) -> dict:
    """Obtiene credenciales de Facebook de un cliente"""
    conn = get_db_connection()
    
    if IS_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT fb_app_id, fb_access_token, fb_account_id FROM users WHERE id = %s",
            (user_id,)
        )
    else:
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
    return {}


def save_user_credentials(user_id: int, fb_app_id: str, fb_token: str, fb_account: str):
    """Guarda credenciales (alias)"""
    update_user_credentials(user_id, fb_app_id, fb_token, fb_account)


# ========== LOGS ==========

def log_access(user_id: int, action: str, ip: str):
    """Registra un acceso en el log"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if IS_POSTGRES:
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
    finally:
        conn.close()


def get_recent_logs(limit: int = 10) -> list:
    """Obtiene los últimos logs de acceso"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if IS_POSTGRES:
        cursor.execute("""
            SELECT l.*, u.email 
            FROM access_logs l
            LEFT JOIN users u ON l.user_id = u.id
            ORDER BY l.timestamp DESC
            LIMIT %s
        """, (limit,))
    else:
        cursor.execute("""
            SELECT l.*, u.email 
            FROM access_logs l
            LEFT JOIN users u ON l.user_id = u.id
            ORDER BY l.timestamp DESC
            LIMIT ?
        """, (limit,))
    
    logs = cursor.fetchall()
    conn.close()
    
    return [dict(log) for log in logs]