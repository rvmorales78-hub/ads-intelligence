# reset_admin_endpoint.py
import streamlit as st
import sqlite3
import hashlib
import os

def reset_admin():
    """Resetea el administrador en la base de datos"""
    
    # Determinar la ruta de la base de datos
    if os.environ.get('RENDER'):
        db_path = '/data/users.db'
    else:
        db_path = 'data/users.db'
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
    
    # Conectar a la BD
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tablas si no existen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY,
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
    
    # Datos del admin
    admin_email = "admin@adsintelligence.com"
    admin_password = "admin123"
    admin_password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
    
    # Verificar si ya existe
    cursor.execute("SELECT id, email FROM admin WHERE email = ?", (admin_email,))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute(
            "UPDATE admin SET password_hash = ? WHERE email = ?",
            (admin_password_hash, admin_email)
        )
        status = "actualizado"
    else:
        cursor.execute(
            "INSERT INTO admin (email, password_hash) VALUES (?, ?)",
            (admin_email, admin_password_hash)
        )
        status = "creado"
    
    conn.commit()
    conn.close()
    
    return status, admin_email, admin_password

# Página de Streamlit
st.set_page_config(page_title="Reset Admin", page_icon="🔧", layout="centered")

st.title("🔧 Herramienta de Reseteo")
st.markdown("Usa esta página para resetear el administrador del sistema.")

if st.button("🚀 Resetear Administrador", use_container_width=True):
    with st.spinner("Procesando..."):
        status, email, password = reset_admin()
        if status == "creado":
            st.success(f"✅ Administrador {status} exitosamente!")
        else:
            st.success(f"✅ Administrador {status} exitosamente!")
        st.code(f"Email: {email}\nContraseña: {password}")
        st.info("Ahora puedes cerrar sesión y volver a entrar con estas credenciales.")

st.markdown("---")
st.caption("Esta página es temporal. Puedes eliminarla después de usarla.")
