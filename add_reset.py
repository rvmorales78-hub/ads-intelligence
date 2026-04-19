import secrets
from datetime import datetime, timedelta

def run():
    with open('database.py', 'r', encoding='utf-8') as f:
        content = f.read()

    new_table = """    'password_resets': '''
        CREATE TABLE IF NOT EXISTS password_resets (
            id {serial_pk},
            email TEXT NOT NULL,
            token TEXT NOT NULL UNIQUE,
            created_at {timestamp_default},
            expires_at {timestamp}
        )
    ''',
    'completed_actions':"""

    if "'password_resets':" not in content:
        content = content.replace("    'completed_actions':", new_table)

    new_funcs = """

# ========== RECUPERACIÓN DE CONTRASEÑA ==========
import secrets
from datetime import datetime, timedelta

def get_user_by_email(email: str):
    with managed_cursor() as cursor:
        q = "SELECT * FROM users WHERE email = %s" if IS_POSTGRES else "SELECT * FROM users WHERE email = ?"
        cursor.execute(q, (email,))
        row = cursor.fetchone()
        if row:
            cols = [desc[0] for desc in cursor.description]
            return dict(zip(cols, row))
        return None

def create_password_reset_token(email: str) -> str:
    user = get_user_by_email(email)
    if not user:
        return None
    token = secrets.token_urlsafe(32)
    expires = datetime.now() + timedelta(hours=24)
    with managed_cursor(commit=True) as cursor:
        q_del = "DELETE FROM password_resets WHERE email = %s" if IS_POSTGRES else "DELETE FROM password_resets WHERE email = ?"
        cursor.execute(q_del, (email,))
        q_ins = "INSERT INTO password_resets (email, token, expires_at) VALUES (%s, %s, %s)" if IS_POSTGRES else "INSERT INTO password_resets (email, token, expires_at) VALUES (?, ?, ?)"
        cursor.execute(q_ins, (email, token, expires))
    return token

def verify_and_reset_password(token: str, new_password: str) -> bool:
    with managed_cursor(commit=True) as cursor:
        q_sel = "SELECT email, expires_at FROM password_resets WHERE token = %s" if IS_POSTGRES else "SELECT email, expires_at FROM password_resets WHERE token = ?"
        cursor.execute(q_sel, (token,))
        row = cursor.fetchone()
        if not row:
            return False
        
        email = row[0]
        expires_at = row[1]
        
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at.replace('Z', ''))
            except ValueError:
                pass
        
        if isinstance(expires_at, datetime) and datetime.now() > expires_at:
            return False
            
        hashed_pw = hash_password(new_password)
        
        q_upd = "UPDATE users SET password_hash = %s WHERE email = %s" if IS_POSTGRES else "UPDATE users SET password_hash = ? WHERE email = ?"
        cursor.execute(q_upd, (hashed_pw, email))
        
        q_del = "DELETE FROM password_resets WHERE email = %s" if IS_POSTGRES else "DELETE FROM password_resets WHERE email = ?"
        cursor.execute(q_del, (email,))
        return True
"""
    if "# ========== RECUPERACIÓN DE CONTRASEÑA" not in content:
        content += new_funcs

    with open('database.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Database functions added.")

run()