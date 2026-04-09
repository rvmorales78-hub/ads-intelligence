import streamlit as st
from database import (
    get_all_users,
    create_user,
    delete_user,
    update_user_credentials,
    update_user_plan,
    get_recent_logs,
    log_access,
)
from auth import require_admin, logout

def admin_dashboard():
    require_admin()
    
    # st.set_page_config(page_title="Admin Panel", page_icon="👑", layout="wide")
    
    st.title("👑 Panel de Administración")
    st.caption("Gestión de usuarios y configuración del sistema")
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"**Admin:** {st.session_state.get('admin_email', '')}")
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            logout()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["👥 Usuarios", "➕ Crear Usuario", "📊 Estadísticas"])
    
    with tab1:
        st.subheader("Usuarios Registrados")
        
        users = get_all_users()
        if users:
            for user in users:
                with st.expander(f"📧 {user['email']} - {user['company_name']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Plan:** {user['plan']}")
                        st.write(f"**Activo:** {'✅' if user['is_active'] else '❌'}")
                        st.write(f"**Creado:** {user['created_at']}")
                        st.write(f"**Último acceso:** {user['last_login']}")
                    
                    with col2:
                        if st.button(f"🗑️ Eliminar", key=f"del_{user['id']}"):
                            delete_user(user['id'])
                            st.rerun()
                    
                    with st.expander("📦 Cambiar Plan"):
                        new_plan = st.selectbox(
                            "Seleccionar nuevo plan",
                            ["basic", "pro", "enterprise"],
                            index=["basic", "pro", "enterprise"].index(user['plan']) if user['plan'] in ["basic", "pro", "enterprise"] else 0,
                            key=f"plan_{user['id']}"
                        )
                        if st.button(f"Actualizar Plan", key=f"update_plan_{user['id']}"):
                            update_user_plan(user['id'], new_plan)
                            st.success(f"Plan actualizado a {new_plan}")
                            st.rerun()
                    
                    # Configurar credenciales de Facebook
                    with st.expander("🔑 Configurar credenciales Facebook"):
                        fb_app_id = st.text_input("App ID", key=f"app_{user['id']}")
                        fb_token = st.text_input("Access Token", type="password", key=f"token_{user['id']}")
                        fb_account = st.text_input("Account ID (act_...)", key=f"acc_{user['id']}")
                        
                        if st.button("💾 Guardar credenciales", key=f"save_{user['id']}"):
                            update_user_credentials(user['id'], fb_app_id, fb_token, fb_account)
                            st.success("Credenciales guardadas")
        else:
            st.info("No hay usuarios registrados")
    
    with tab2:
        st.subheader("Crear Nuevo Usuario")
        
        with st.form("create_user_form"):
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            company = st.text_input("Nombre de la empresa")
            plan = st.selectbox("Plan", ["basic", "pro", "enterprise"])
            
            submitted = st.form_submit_button("Crear Usuario")
            
            if submitted:
                if create_user(email, password, company, plan):
                    st.success(f"Usuario {email} creado exitosamente")
                    st.rerun()
                else:
                    st.error("Email ya existe")
    
    with tab3:
        st.subheader("Estadísticas del Sistema")
        
        users = get_all_users()
        st.metric("Total Usuarios", len(users))
        st.metric("Usuarios Activos", sum(1 for u in users if u['is_active']))
        
        st.markdown("---")
        st.subheader("📋 Últimos Accesos")
        
        logs = get_recent_logs(limit=10)
        if logs:
            for log in logs:
                st.caption(f"🕐 {log['timestamp']} - {log['email']} - {log['action']}")
        else:
            st.info("No hay registros de acceso")