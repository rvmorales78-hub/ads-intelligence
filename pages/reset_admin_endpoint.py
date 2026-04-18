# reset_admin_endpoint.py
import streamlit as st
import sqlite3
import os
import sys

# Añadir el directorio raíz al path para poder importar 'database'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import hash_password

st.title("🔧 Herramienta de Reseteo")
st.markdown("Usa esta página para resetear el administrador del sistema.")

if st.button("🚀 Resetear Administrador", use_container_width=True):
    with st.spinner("Procesando..."):
        # Usar directorio local en lugar de /data
        db_path = 'data/users.db'
        
        # Crear directorio data local
        os.makedirs('data', exist_ok=True)
        
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
        admin_password_hash = hash_password(admin_password)
        
        # Resetear admin
        cursor.execute("DELETE FROM admin WHERE email = ?", (admin_email,))
        cursor.execute(
            "INSERT INTO admin (email, password_hash) VALUES (?, ?)",
            (admin_email, admin_password_hash)
        )
        
        conn.commit()
        conn.close()
        
        st.success("✅ Administrador reseteado exitosamente!")
        st.code(f"Email: {admin_email}\nContraseña: {admin_password}")
        st.info("Ahora puedes cerrar sesión y volver a entrar con estas credenciales.")

st.markdown("---")
st.caption("Esta página es temporal. Puedes eliminarla después de usarla.")