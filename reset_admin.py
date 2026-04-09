# reset_admin.py
import sqlite3
import hashlib
import os

def reset_admin():
    """Resetea o crea el administrador por defecto"""
    
    # Determinar la ruta de la base de datos
    if os.environ.get('RENDER'):
        db_path = '/data/users.db'
    else:
        db_path = 'data/users.db'
    
    # Verificar si el archivo existe
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada en: {db_path}")
        print("   Ejecuta la aplicación al menos una vez para crear la BD")
        return
    
    # Conectar a la BD
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar si la tabla admin existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin'")
    if not cursor.fetchone():
        print("❌ Tabla 'admin' no existe. Creándola...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        conn.commit()
    
    # Datos del admin
    admin_email = "admin@adsintelligence.com"
    admin_password = "admin123"
    admin_password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
    
    # Verificar si ya existe
    cursor.execute("SELECT id, email FROM admin WHERE email = ?", (admin_email,))
    existing = cursor.fetchone()
    
    if existing:
        # Actualizar contraseña
        cursor.execute(
            "UPDATE admin SET password_hash = ? WHERE email = ?",
            (admin_password_hash, admin_email)
        )
        print(f"✅ Admin actualizado: {admin_email} / {admin_password}")
    else:
        # Crear nuevo admin
        cursor.execute(
            "INSERT INTO admin (email, password_hash) VALUES (?, ?)",
            (admin_email, admin_password_hash)
        )
        print(f"✅ Admin creado: {admin_email} / {admin_password}")
    
    conn.commit()
    conn.close()
    
    # Verificar que funciona
    verify = hashlib.sha256(admin_password.encode()).hexdigest()
    print(f"   Hash: {verify[:20]}...")

if __name__ == "__main__":
    reset_admin()