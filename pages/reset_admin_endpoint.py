# reset_admin_endpoint.py
import streamlit as st
import sqlite3
import hashlib
import os

# No llamar a set_page_config aquí

st.title("🔧 Herramienta de Reseteo")
st.markdown("Usa esta página para resetear el administrador del sistema.")

if st.button("🚀 Resetear Administrador", use_container_width=True):
    with st.spinner("Procesando..."):
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
        
        # Datos del admin
        admin_email = "admin@adsintelligence.com"
        admin_password = "admin123"
        admin_password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
        
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

st.markdown("---")
st.caption("Esta página es temporal. Puedes eliminarla después de usarla.")