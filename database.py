import os
import hashlib
from datetime import datetime, date, timedelta
from contextlib import contextmanager

# NUEVO: Usar passlib para hashing seguro de contraseñas
try:
    from passlib.context import CryptContext
    PASSLIB_AVAILABLE = True
    # Configurar el contexto una sola vez, usando bcrypt que es el estándar recomendado
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except ImportError:
    PASSLIB_AVAILABLE = False
    pwd_context = None
    print("ADVERTENCIA: passlib no está instalado. El hashing de contraseñas será inseguro.")

# Intentar importar psycopg2 para PostgreSQL
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    psycopg2 = None
    RealDictCursor = None
    PSYCOPG2_AVAILABLE = False

DATABASE_URL = os.getenv('DATABASE_URL', '')
IS_POSTGRES = bool(DATABASE_URL and PSYCOPG2_AVAILABLE)

# ========== CONEXIÓN Y MANEJO DE CURSOR (REFACTORIZADO) ==========

def get_db_connection():
    """Retorna conexión a PostgreSQL o SQLite según entorno"""
    if IS_POSTGRES:
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    else:
        import sqlite3
        db_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(os.path.join(db_dir, 'users.db'))
        # Para sqlite3, la row_factory se establece en la conexión para que devuelva dicts
        conn.row_factory = sqlite3.Row
        return conn

@contextmanager
def managed_cursor(commit=False, as_dict=False):
    """
    Context manager para manejar conexiones y cursores de forma segura.
    Asegura que la conexión se cierre siempre.
    """
    conn = get_db_connection()
    cursor = None
    try:
        # Para PostgreSQL, el cursor tipo diccionario se especifica en su creación
        if IS_POSTGRES and as_dict:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        
        yield cursor
        
        if commit:
            conn.commit()
    except Exception as e:
        print(f"Error en la base de datos: {e}") # Idealmente, usar logging
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def get_user_with_trial_info(user_id: int) -> dict | None:
    """Obtiene un usuario por su ID incluyendo la fecha de inicio de la prueba (created_at)"""
    sql = "SELECT *, created_at as trial_start_date FROM users WHERE id = %s" if IS_POSTGRES else "SELECT *, created_at FROM users WHERE id = ?"
    with managed_cursor(as_dict=True) as cursor:
        cursor.execute(sql, (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None

# ========== SEGURIDAD (REFACTORIZADO) ==========

def hash_password(password: str) -> str:
    """Hashea una contraseña de forma segura con bcrypt usando passlib."""
    if not PASSLIB_AVAILABLE or not pwd_context:
        return hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña plana contra su hash seguro."""
    if not PASSLIB_AVAILABLE or not pwd_context or not hashed_password.startswith('$2b$'):
        # Fallback para contraseñas antiguas hasheadas con SHA256
        return hashed_password == hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(plain_password, hashed_password)

# ========== INICIALIZACIÓN ==========

def init_db():
    """Inicializa las tablas según el motor de BD"""
    with managed_cursor(commit=True) as cursor:
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
                fb_account_id TEXT,
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT
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

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS fb_accounts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                account_name TEXT DEFAULT '',
                app_id_enc TEXT NOT NULL,
                access_token_enc TEXT NOT NULL,
                account_id_enc TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_actions_daily (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                kill_count INTEGER DEFAULT 0,
                fix_count INTEGER DEFAULT 0,
                scale_count INTEGER DEFAULT 0,
                account_score INTEGER DEFAULT 0,
                total_actions INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date)
            )
        ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                score INTEGER DEFAULT 0,
                actions_completed INTEGER DEFAULT 0,
                improvements_made INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS completed_actions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                campaign_name TEXT NOT NULL,
                action_text TEXT NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                marked_done_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                fb_account_id TEXT,
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT
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

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS fb_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                account_name TEXT DEFAULT '',
                app_id_enc TEXT NOT NULL,
                access_token_enc TEXT NOT NULL,
                account_id_enc TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_actions_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                kill_count INTEGER DEFAULT 0,
                fix_count INTEGER DEFAULT 0,
                scale_count INTEGER DEFAULT 0,
                account_score INTEGER DEFAULT 0,
                total_actions INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date)
            )
        ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                score INTEGER DEFAULT 0,
                actions_completed INTEGER DEFAULT 0,
                improvements_made INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS completed_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action_type TEXT NOT NULL, -- 'kill', 'fix', 'scale'
                campaign_name TEXT NOT NULL,
                action_text TEXT NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                marked_done_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Migración: agregar columna account_name si no existe (tabla creada antes del multi-cuenta)
        try:
            if IS_POSTGRES:
                cursor.execute("""
                    ALTER TABLE fb_accounts ADD COLUMN IF NOT EXISTS account_name TEXT DEFAULT ''
                """)
            else:
                # SQLite no tiene ADD COLUMN IF NOT EXISTS — verificar primero
                cursor.execute("PRAGMA table_info(fb_accounts)")
                existing_cols = [row[1] for row in cursor.fetchall()]
                if 'account_name' not in existing_cols:
                    cursor.execute("ALTER TABLE fb_accounts ADD COLUMN account_name TEXT DEFAULT ''")
        except Exception:
            pass  # La tabla puede no existir aún; init_db la creará con la columna

        # Crear admin por defecto si no existe
        admin_password_hash = hash_password("admin123")
        
        sql_select = "SELECT * FROM admin WHERE email = %s" if IS_POSTGRES else "SELECT * FROM admin WHERE email = ?"
        cursor.execute(sql_select, ("admin@adsintelligence.com",))
        
        if not cursor.fetchone():
            sql_insert = "INSERT INTO admin (email, password_hash) VALUES (%s, %s)" if IS_POSTGRES else "INSERT INTO admin (email, password_hash) VALUES (?, ?)"
            cursor.execute(sql_insert, ("admin@adsintelligence.com", admin_password_hash))


# ========== VERIFICACIONES ==========

def verify_user(email: str, password: str) -> dict | None:
    """Verifica credenciales de un cliente de forma segura."""
    print('>>> verify_user llamada')
    
    # Paso 1: Obtener el usuario
    sql_select = "SELECT * FROM users WHERE email = %s AND is_active = 1" if IS_POSTGRES else "SELECT * FROM users WHERE email = ? AND is_active = 1"
    user = None
    with managed_cursor(as_dict=True) as cursor:
        cursor.execute(sql_select, (email,))
        user_data = cursor.fetchone()
        if user_data:
            user = dict(user_data)

    if not user:
        return None

    # Paso 2: Verificar la contraseña de forma segura
    if not verify_password(password, user['password_hash']):
        return None

    # Paso 3: Si la verificación es exitosa, actualizar last_login
    sql_update = "UPDATE users SET last_login = %s WHERE id = %s" if IS_POSTGRES else "UPDATE users SET last_login = ? WHERE id = ?"
    with managed_cursor(commit=True) as cursor:
        cursor.execute(sql_update, (datetime.now(), user['id']))
    
    return user


def verify_admin(email: str, password: str) -> dict | None:
    print('>>> verify_admin llamada')
    """Verifica credenciales de administrador"""
    sql = "SELECT * FROM admin WHERE email = %s" if IS_POSTGRES else "SELECT * FROM admin WHERE email = ?"
    with managed_cursor(as_dict=True) as cursor:
        cursor.execute(sql, (email,))
        admin = cursor.fetchone()
        if admin and verify_password(password, admin['password_hash']):
            return dict(admin)
    return None


# ========== CRUD USUARIOS ==========

def create_user(email: str, password: str, company_name: str, plan: str = 'basic') -> bool:
    """Crea un nuevo usuario cliente"""
    hashed_password = hash_password(password)
    sql = "INSERT INTO users (email, password_hash, company_name, plan) VALUES (%s, %s, %s, %s)" if IS_POSTGRES else "INSERT INTO users (email, password_hash, company_name, plan) VALUES (?, ?, ?, ?)"
    try:
        with managed_cursor(commit=True) as cursor:
            cursor.execute(sql, (email, hashed_password, company_name, plan))
        return True
    except Exception:
        # El context manager ya maneja el rollback y cierre
        return False


def get_all_users() -> list:
    """Obtiene todos los usuarios clientes"""
    sql = "SELECT id, email, company_name, plan, is_active, created_at, last_login FROM users"
    with managed_cursor(as_dict=True) as cursor:
        cursor.execute(sql)
        users = cursor.fetchall()
        return [dict(user) for user in users]


def get_user_by_id(user_id: int) -> dict | None:
    """Obtiene un usuario por su ID"""
    sql = "SELECT * FROM users WHERE id = %s" if IS_POSTGRES else "SELECT * FROM users WHERE id = ?"
    with managed_cursor(as_dict=True) as cursor:
        cursor.execute(sql, (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None


def delete_user(user_id: int):
    """Elimina un usuario"""
    sql = "DELETE FROM users WHERE id = %s" if IS_POSTGRES else "DELETE FROM users WHERE id = ?"
    with managed_cursor(commit=True) as cursor:
        cursor.execute(sql, (user_id,))


def update_user_plan(user_id: int, new_plan: str):
    """Actualiza el plan de un usuario"""
    sql = "UPDATE users SET plan = %s WHERE id = %s" if IS_POSTGRES else "UPDATE users SET plan = ? WHERE id = ?"
    with managed_cursor(commit=True) as cursor:
        cursor.execute(sql, (new_plan, user_id))


# ========== GESTIÓN DE CUENTAS FACEBOOK MULTI-USUARIO ==========
def add_fb_account(user_id: int, app_id_enc: str, token_enc: str, account_id_enc: str, account_name: str = ''):
    """Guarda una nueva cuenta de Facebook"""
    sql = "INSERT INTO fb_accounts (user_id, account_name, app_id_enc, access_token_enc, account_id_enc) VALUES (%s, %s, %s, %s, %s)" if IS_POSTGRES else "INSERT INTO fb_accounts (user_id, account_name, app_id_enc, access_token_enc, account_id_enc) VALUES (?, ?, ?, ?, ?)"
    with managed_cursor(commit=True) as cursor:
        cursor.execute(sql, (user_id, account_name, app_id_enc, token_enc, account_id_enc))

def get_fb_accounts(user_id: int):
    """Obtiene todas las cuentas de Facebook de un usuario"""
    sql = "SELECT id, account_name, app_id_enc, access_token_enc, account_id_enc FROM fb_accounts WHERE user_id = %s ORDER BY id" if IS_POSTGRES else "SELECT id, account_name, app_id_enc, access_token_enc, account_id_enc FROM fb_accounts WHERE user_id = ? ORDER BY id"
    with managed_cursor(as_dict=True) as cursor:
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_all_system_fb_accounts():
    """Obtiene TODAS las cuentas de Facebook registradas en el sistema (para verificar duplicados)"""
    sql = "SELECT user_id, account_id_enc FROM fb_accounts"
    with managed_cursor(as_dict=True) as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def delete_fb_account(account_db_id: int):
    """Elimina una cuenta de Facebook"""
    sql = "DELETE FROM fb_accounts WHERE id = %s" if IS_POSTGRES else "DELETE FROM fb_accounts WHERE id = ?"
    with managed_cursor(commit=True) as cursor:
        cursor.execute(sql, (account_db_id,))

def delete_all_fb_accounts(user_id: int):
    """Elimina todas las cuentas de Facebook de un usuario"""
    sql = "DELETE FROM fb_accounts WHERE user_id = %s" if IS_POSTGRES else "DELETE FROM fb_accounts WHERE user_id = ?"
    with managed_cursor(commit=True) as cursor:
        cursor.execute(sql, (user_id,))

def update_user_stripe_info(user_id: int, customer_id: str, subscription_id: str):
    """Guarda el ID de cliente y suscripción de Stripe para un usuario"""
    sql = "UPDATE users SET stripe_customer_id = %s, stripe_subscription_id = %s WHERE id = %s" if IS_POSTGRES else "UPDATE users SET stripe_customer_id = ?, stripe_subscription_id = ? WHERE id = ?"
    try:
        with managed_cursor(commit=True) as cursor:
            cursor.execute(sql, (customer_id, subscription_id, user_id))
    except Exception as e:
        print(f"Error actualizando info de Stripe: {e}")


# ========== GESTIÓN DE ACCIONES DIARIAS Y PROGRESO ==========

def save_daily_actions_summary(user_id: int, date: str, kill_count: int, fix_count: int, scale_count: int, account_score: int):
    """Guarda o actualiza el resumen diario de acciones para un usuario"""
    total_actions = kill_count + fix_count + scale_count

    try:
        with managed_cursor(commit=True) as cursor:
            if IS_POSTGRES:
                cursor.execute("""
                    INSERT INTO user_actions_daily (user_id, date, kill_count, fix_count, scale_count, account_score, total_actions)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, date) DO UPDATE SET
                    kill_count = EXCLUDED.kill_count,
                    fix_count = EXCLUDED.fix_count,
                    scale_count = EXCLUDED.scale_count,
                    account_score = EXCLUDED.account_score,
                    total_actions = EXCLUDED.total_actions
                """, (user_id, date, kill_count, fix_count, scale_count, account_score, total_actions))
            else:
                cursor.execute("""
                    INSERT OR REPLACE INTO user_actions_daily (user_id, date, kill_count, fix_count, scale_count, account_score, total_actions)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, date, kill_count, fix_count, scale_count, account_score, total_actions))
    except Exception as e:
        print(f"Error saving daily actions: {e}")


def get_today_actions_summary(user_id: int):
    """Obtiene el resumen de acciones de hoy para un usuario"""
    try:
        today = datetime.now().date().isoformat()
        sql = "SELECT * FROM user_actions_daily WHERE user_id = %s AND date = %s" if IS_POSTGRES else "SELECT * FROM user_actions_daily WHERE user_id = ? AND date = ?"
        with managed_cursor(as_dict=True) as cursor:
            cursor.execute(sql, (user_id, today))
            result = cursor.fetchone()
            return dict(result) if result else None
    except Exception as e:
        print(f"Error getting today's actions: {e}")
        return None


def get_last_week_actions(user_id: int):
    """Obtiene los resúmenes de acciones de la última semana"""
    try:
        start_date = date.today() - timedelta(days=7)
        sql = "SELECT * FROM user_actions_daily WHERE user_id = %s AND date >= %s ORDER BY date DESC" if IS_POSTGRES else "SELECT * FROM user_actions_daily WHERE user_id = ? AND date >= ? ORDER BY date DESC"
        with managed_cursor(as_dict=True) as cursor:
            cursor.execute(sql, (user_id, start_date))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting last week actions: {e}")
        return []


def save_user_progress(user_id: int, date: str, score: int, actions_completed: int = 0, improvements_made: int = 0, notes: str = ""):
    """Guarda el progreso diario de un usuario"""
    try:
        sql = "INSERT INTO user_progress (user_id, date, score, actions_completed, improvements_made, notes) VALUES (%s, %s, %s, %s, %s, %s)" if IS_POSTGRES else "INSERT INTO user_progress (user_id, date, score, actions_completed, improvements_made, notes) VALUES (?, ?, ?, ?, ?, ?)"
        with managed_cursor(commit=True) as cursor:
            cursor.execute(sql, (user_id, date, score, actions_completed, improvements_made, notes))
    except Exception as e:
        print(f"Error saving user progress: {e}")


def get_user_progress_history(user_id: int, days: int = 30):
    """Obtiene el historial de progreso de un usuario"""
    try:
        start_date = date.today() - timedelta(days=days)
        sql = "SELECT * FROM user_progress WHERE user_id = %s AND date >= %s ORDER BY date DESC" if IS_POSTGRES else "SELECT * FROM user_progress WHERE user_id = ? AND date >= ? ORDER BY date DESC"
        with managed_cursor(as_dict=True) as cursor:
            cursor.execute(sql, (user_id, start_date))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting user progress: {e}")
        return []


def mark_action_as_completed(user_id: int, action_type: str, campaign_name: str, action_text: str):
    """Marca una acción como completada por el usuario"""
    try:
        sql = "INSERT INTO completed_actions (user_id, action_type, campaign_name, action_text) VALUES (%s, %s, %s, %s)" if IS_POSTGRES else "INSERT INTO completed_actions (user_id, action_type, campaign_name, action_text) VALUES (?, ?, ?, ?)"
        with managed_cursor(commit=True) as cursor:
            cursor.execute(sql, (user_id, action_type, campaign_name, action_text))
    except Exception as e:
        print(f"Error marking action as completed: {e}")


def get_completed_actions(user_id: int, days: int = 7):
    """Obtiene las acciones completadas por un usuario"""
    try:
        start_date = date.today() - timedelta(days=days)
        sql = "SELECT * FROM completed_actions WHERE user_id = %s AND completed_at >= %s ORDER BY completed_at DESC" if IS_POSTGRES else "SELECT * FROM completed_actions WHERE user_id = ? AND completed_at >= ? ORDER BY completed_at DESC"
        with managed_cursor(as_dict=True) as cursor:
            cursor.execute(sql, (user_id, start_date))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting completed actions: {e}")
        return []


def get_total_completed_actions(user_id: int):
    """Obtiene el total de acciones completadas por un usuario"""
    try:
        sql = "SELECT COUNT(*) as total FROM completed_actions WHERE user_id = %s" if IS_POSTGRES else "SELECT COUNT(*) as total FROM completed_actions WHERE user_id = ?"
        with managed_cursor(as_dict=True) as cursor:
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            return result['total'] if result else 0
    except Exception as e:
        print(f"Error getting total completed actions: {e}")
        return 0


# ========== COMPATIBILIDAD PARA AUTH.PY ==========
def get_user_credentials(user_id: int):
    """Devuelve las credenciales de la primera cuenta de Facebook del usuario (para compatibilidad)"""
    print('>>> get_user_credentials llamada')
    accounts = get_fb_accounts(user_id)
    if accounts:
        return {
            'fb_app_id': accounts[0]['app_id_enc'],
            'fb_access_token': accounts[0]['access_token_enc'],
            'fb_account_id': accounts[0]['account_id_enc']
        }
    return {'fb_app_id': '', 'fb_access_token': '', 'fb_account_id': ''}


# ========== LOG DE ACCESOS ==========
def log_access(user_id: int, action: str, ip: str):
    """Registra un acceso de usuario en la tabla access_logs"""
    print('>>> log_access llamada')
    sql = "INSERT INTO access_logs (user_id, action, ip_address) VALUES (%s, %s, %s)" if IS_POSTGRES else "INSERT INTO access_logs (user_id, action, ip_address) VALUES (?, ?, ?)"
    with managed_cursor(commit=True) as cursor:
        cursor.execute(sql, (user_id, action, ip))


# ============================================================
# Funciones de compatibilidad para auth.py (si se requieren)
# ============================================================
def save_user_credentials(user_id: int, fb_app_id_enc: str, fb_token_enc: str, fb_account_enc: str, account_name: str = ''):
    """Guarda una nueva cuenta de Facebook (wrapper para compatibilidad)"""
    add_fb_account(user_id, fb_app_id_enc, fb_token_enc, fb_account_enc, account_name)

def update_user_credentials(user_id: int, fb_app_id: str, fb_token: str, fb_account: str):
    """Reemplaza TODAS las cuentas de Facebook de un usuario con una única cuenta (usado por el panel de admin)"""
    delete_all_fb_accounts(user_id)
    if fb_app_id and fb_token and fb_account:
        add_fb_account(user_id, fb_app_id, fb_token, fb_account, account_name='Principal')

def get_recent_logs(limit=10):
    """Obtiene los últimos accesos con email de usuario"""
    try:
        sql = """SELECT al.timestamp, al.action, al.ip_address, u.email
                   FROM access_logs al
                   LEFT JOIN users u ON al.user_id = u.id
                   ORDER BY al.timestamp DESC LIMIT """ + ("%s" if IS_POSTGRES else "?")
        with managed_cursor(as_dict=True) as cursor:
            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception:
        return []