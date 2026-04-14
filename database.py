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
    print('>>> verify_user llamada')
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
    print('>>> verify_admin llamada')
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


# ========== GESTIÓN DE CUENTAS FACEBOOK MULTI-USUARIO ==========
def add_fb_account(user_id: int, app_id_enc: str, token_enc: str, account_id_enc: str, account_name: str = ''):
    """Guarda una nueva cuenta de Facebook"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if IS_POSTGRES:
        cursor.execute(
            "INSERT INTO fb_accounts (user_id, account_name, app_id_enc, access_token_enc, account_id_enc) VALUES (%s, %s, %s, %s, %s)",
            (user_id, account_name, app_id_enc, token_enc, account_id_enc)
        )
    else:
        cursor.execute(
            "INSERT INTO fb_accounts (user_id, account_name, app_id_enc, access_token_enc, account_id_enc) VALUES (?, ?, ?, ?, ?)",
            (user_id, account_name, app_id_enc, token_enc, account_id_enc)
        )
    conn.commit()
    conn.close()

def get_fb_accounts(user_id: int):
    """Obtiene todas las cuentas de Facebook de un usuario"""
    conn = get_db_connection()
    if IS_POSTGRES:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT id, account_name, app_id_enc, access_token_enc, account_id_enc FROM fb_accounts WHERE user_id = %s ORDER BY id",
            (user_id,)
        )
    else:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, account_name, app_id_enc, access_token_enc, account_id_enc FROM fb_accounts WHERE user_id = ? ORDER BY id",
            (user_id,)
        )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_fb_account(account_db_id: int):
    """Elimina una cuenta de Facebook"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if IS_POSTGRES:
        cursor.execute("DELETE FROM fb_accounts WHERE id = %s", (account_db_id,))
    else:
        cursor.execute("DELETE FROM fb_accounts WHERE id = ?", (account_db_id,))
    conn.commit()
    conn.close()

def delete_all_fb_accounts(user_id: int):
    """Elimina todas las cuentas de Facebook de un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if IS_POSTGRES:
        cursor.execute("DELETE FROM fb_accounts WHERE user_id = %s", (user_id,))
    else:
        cursor.execute("DELETE FROM fb_accounts WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# ========== GESTIÓN DE ACCIONES DIARIAS Y PROGRESO ==========

def save_daily_actions_summary(user_id: int, date: str, kill_count: int, fix_count: int, scale_count: int, account_score: int):
    """Guarda o actualiza el resumen diario de acciones para un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()

    total_actions = kill_count + fix_count + scale_count

    try:
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
        conn.commit()
    except Exception as e:
        print(f"Error saving daily actions: {e}")
    finally:
        conn.close()


def get_today_actions_summary(user_id: int):
    """Obtiene el resumen de acciones de hoy para un usuario"""
    conn = get_db_connection()

    try:
        today = datetime.now().date().isoformat()

        if IS_POSTGRES:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM user_actions_daily
                WHERE user_id = %s AND date = %s
            """, (user_id, today))
        else:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM user_actions_daily
                WHERE user_id = ? AND date = ?
            """, (user_id, today))

        result = cursor.fetchone()
        return dict(result) if result else None
    except Exception as e:
        print(f"Error getting today's actions: {e}")
        return None
    finally:
        conn.close()


def get_last_week_actions(user_id: int):
    """Obtiene los resúmenes de acciones de la última semana"""
    conn = get_db_connection()

    try:
        if IS_POSTGRES:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM user_actions_daily
                WHERE user_id = %s AND date >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY date DESC
            """, (user_id,))
        else:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM user_actions_daily
                WHERE user_id = ? AND date >= date('now', '-7 days')
                ORDER BY date DESC
            """, (user_id,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting last week actions: {e}")
        return []
    finally:
        conn.close()


def save_user_progress(user_id: int, date: str, score: int, actions_completed: int = 0, improvements_made: int = 0, notes: str = ""):
    """Guarda el progreso diario de un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if IS_POSTGRES:
            cursor.execute("""
                INSERT INTO user_progress (user_id, date, score, actions_completed, improvements_made, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, date, score, actions_completed, improvements_made, notes))
        else:
            cursor.execute("""
                INSERT INTO user_progress (user_id, date, score, actions_completed, improvements_made, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, date, score, actions_completed, improvements_made, notes))
        conn.commit()
    except Exception as e:
        print(f"Error saving user progress: {e}")
    finally:
        conn.close()


def get_user_progress_history(user_id: int, days: int = 30):
    """Obtiene el historial de progreso de un usuario"""
    conn = get_db_connection()

    try:
        if IS_POSTGRES:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM user_progress
                WHERE user_id = %s AND date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY date DESC
            """, (user_id, days))
        else:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM user_progress
                WHERE user_id = ? AND date >= date('now', '-? days')
                ORDER BY date DESC
            """, (user_id, days))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting user progress: {e}")
        return []
    finally:
        conn.close()


def mark_action_as_completed(user_id: int, action_type: str, campaign_name: str, action_text: str):
    """Marca una acción como completada por el usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if IS_POSTGRES:
            cursor.execute("""
                INSERT INTO completed_actions (user_id, action_type, campaign_name, action_text)
                VALUES (%s, %s, %s, %s)
            """, (user_id, action_type, campaign_name, action_text))
        else:
            cursor.execute("""
                INSERT INTO completed_actions (user_id, action_type, campaign_name, action_text)
                VALUES (?, ?, ?, ?)
            """, (user_id, action_type, campaign_name, action_text))
        conn.commit()
    except Exception as e:
        print(f"Error marking action as completed: {e}")
    finally:
        conn.close()


def get_completed_actions(user_id: int, days: int = 7):
    """Obtiene las acciones completadas por un usuario"""
    conn = get_db_connection()

    try:
        if IS_POSTGRES:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM completed_actions
                WHERE user_id = %s AND completed_at >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY completed_at DESC
            """, (user_id, days))
        else:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM completed_actions
                WHERE user_id = ? AND completed_at >= date('now', '-? days')
                ORDER BY completed_at DESC
            """, (user_id, days))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting completed actions: {e}")
        return []
    finally:
        conn.close()


def get_total_completed_actions(user_id: int):
    """Obtiene el total de acciones completadas por un usuario"""
    conn = get_db_connection()

    try:
        if IS_POSTGRES:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT COUNT(*) as total FROM completed_actions
                WHERE user_id = %s
            """, (user_id,))
        else:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as total FROM completed_actions
                WHERE user_id = ?
            """, (user_id,))

        result = cursor.fetchone()
        return result['total'] if result else 0
    except Exception as e:
        print(f"Error getting total completed actions: {e}")
        return 0
    finally:
        conn.close()


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
    conn = get_db_connection()
    cursor = conn.cursor()
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
    conn.close()


# ============================================================
# Funciones de compatibilidad para auth.py (si se requieren)
# ============================================================
def save_user_credentials(user_id: int, fb_app_id_enc: str, fb_token_enc: str, fb_account_enc: str, account_name: str = ''):
    """Guarda una nueva cuenta de Facebook (para compatibilidad)"""
    add_fb_account(user_id, fb_app_id_enc, fb_token_enc, fb_account_enc, account_name)

def update_user_credentials(user_id: int, fb_app_id: str, fb_token: str, fb_account: str):
    """Reemplaza TODAS las cuentas de Facebook de un usuario con una única cuenta (usado por admin)"""
    delete_all_fb_accounts(user_id)
    if fb_app_id and fb_token and fb_account:
        add_fb_account(user_id, fb_app_id, fb_token, fb_account, account_name='Principal')

def get_recent_logs(limit=10):
    """Obtiene los últimos accesos con email de usuario"""
    conn = get_db_connection()
    try:
        if IS_POSTGRES:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """SELECT al.timestamp, al.action, al.ip_address, u.email
                   FROM access_logs al
                   LEFT JOIN users u ON al.user_id = u.id
                   ORDER BY al.timestamp DESC LIMIT %s""",
                (limit,)
            )
        else:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT al.timestamp, al.action, al.ip_address, u.email
                   FROM access_logs al
                   LEFT JOIN users u ON al.user_id = u.id
                   ORDER BY al.timestamp DESC LIMIT ?""",
                (limit,)
            )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception:
        return []
    finally:
        conn.close()