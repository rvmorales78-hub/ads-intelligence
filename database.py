import sqlite3
import hashlib
import os
from datetime import datetime
from contextlib import contextmanager


def get_db_path():
    """Retorna la ruta correcta para la base de datos según el entorno"""
    # Para producción en Render, usamos /data/ (disco persistente)
    if os.environ.get('RENDER'):
        data_dir = '/data'
    else:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')

    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'users.db')


def init_db():
    """Inicializa la base de datos con todas las tablas"""
    DATABASE_PATH = get_db_path()
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        # Tabla de usuarios (clientes)
        conn.execute('''
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
        
        # Tabla de administradores
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        
        # Tabla de logs de acceso
        conn.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear admin por defecto si no existe
        admin_exists = conn.execute("SELECT id FROM admin LIMIT 1").fetchone()
        if not admin_exists:
            admin_password = hashlib.sha256("admin123".encode()).hexdigest()
            conn.execute(
                "INSERT INTO admin (email, password_hash) VALUES (?, ?)",
                ("admin@adsintelligence.com", admin_password)
            )
            print("✅ Administrador creado: admin@adsintelligence.com / admin123")


@contextmanager
def get_db():
    """Context manager para conexiones a BD"""
    DATABASE_PATH = get_db_path()
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        yield conn


def hash_password(password: str) -> str:
    """Hashea una contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_user(email: str, password: str) -> dict | None:
    """Verifica credenciales de un cliente"""
    with get_db() as conn:
        user = conn.execute(
            "SELECT id, email, password_hash, company_name, plan, fb_app_id, fb_access_token, fb_account_id, last_login, is_active "
            "FROM users WHERE email = ? AND is_active = 1",
            (email,)
        ).fetchone()
        
        if user and user['password_hash'] == hash_password(password):
            # Actualizar último acceso
            conn.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now(), user['id'])
            )
            return dict(user)
    return None


def verify_admin(email: str, password: str) -> dict | None:
    """Verifica credenciales de administrador"""
    with get_db() as conn:
        admin = conn.execute(
            "SELECT * FROM admin WHERE email = ?",
            (email,)
        ).fetchone()
        
        if admin and admin['password_hash'] == hash_password(password):
            return dict(admin)
    return None


def create_user(email: str, password: str, company_name: str, plan: str = 'basic') -> bool:
    """Crea un nuevo usuario cliente"""
    with get_db() as conn:
        try:
            conn.execute(
                """INSERT INTO users (email, password_hash, company_name, plan) 
                   VALUES (?, ?, ?, ?)""",
                (email, hash_password(password), company_name, plan)
            )
            return True
        except sqlite3.IntegrityError:
            return False


def update_user_credentials(user_id: int, fb_app_id: str, fb_access_token: str, fb_account_id: str):
    """Actualiza credenciales de Facebook de un cliente"""
    with get_db() as conn:
        conn.execute(
            """UPDATE users 
               SET fb_app_id = ?, fb_access_token = ?, fb_account_id = ?
               WHERE id = ?""",
            (fb_app_id, fb_access_token, fb_account_id, user_id)
        )


def get_user_credentials(user_id: int) -> dict:
    """Obtiene credenciales de Facebook de un cliente"""
    with get_db() as conn:
        user = conn.execute(
            "SELECT fb_app_id, fb_access_token, fb_account_id FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        if user:
            return {
                'fb_app_id': user['fb_app_id'] or '',
                'fb_access_token': user['fb_access_token'] or '',
                'fb_account_id': user['fb_account_id'] or ''
            }
        return {}


def save_user_credentials(user_id: int, fb_app_id: str, fb_token: str, fb_account: str):
    """Guarda credenciales (alias de update_user_credentials)"""
    update_user_credentials(user_id, fb_app_id, fb_token, fb_account)


def get_all_users() -> list:
    """Obtiene todos los usuarios clientes"""
    with get_db() as conn:
        return [dict(row) for row in conn.execute(
            "SELECT id, email, company_name, plan, is_active, created_at, last_login FROM users"
        )]


def delete_user(user_id: int):
    """Elimina un usuario"""
    with get_db() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))


def log_access(user_id: int, action: str, ip: str):
    """Registra un acceso en el log"""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO access_logs (user_id, action, ip_address) VALUES (?, ?, ?)",
            (user_id, action, ip)
        )


def update_user_plan(user_id: int, new_plan: str):
    """Actualiza el plan de un usuario"""
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET plan = ? WHERE id = ?",
            (new_plan, user_id)
        )


def get_recent_logs(limit: int = 10) -> list:
    """Obtiene los últimos logs de acceso"""
    with get_db() as conn:
        return [dict(row) for row in conn.execute(
            "SELECT l.*, u.email FROM access_logs l JOIN users u ON l.user_id = u.id ORDER BY l.timestamp DESC LIMIT ?",
            (limit,)
        )]


def get_user_by_id(user_id: int) -> dict | None:
    """Obtiene un usuario por su ID"""
    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return dict(user) if user else None