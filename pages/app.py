import streamlit as st
from auth import login_page
from database import init_db
from admin_dashboard import admin_dashboard
from client_dashboard import client_dashboard

# Inicializar base de datos
init_db()

if 'authenticated' not in st.session_state:
    login_page()
else:
    if st.session_state.get('user_type') == 'admin':
        admin_dashboard()
    else:
        client_dashboard()
