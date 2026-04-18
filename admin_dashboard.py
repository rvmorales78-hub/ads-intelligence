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


ADMIN_DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
body, .stApp { 
    background: #F0F2F5 !important; 
    color: #1c1e21; 
    font-family: 'Roboto', sans-serif;
}
h1,h2,h3,h4 { color: #1c1e21 !important; font-family: 'Segoe UI', 'Roboto', sans-serif; font-weight: 700; }

/* ---- Ocultar Streamlit UI ---- */
#MainMenu, footer { visibility: hidden; }
.stApp > header { display: none; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1280px !important; }

/* ---- Header ---- */
h1 {
    font-family: 'Segoe UI', sans-serif !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #1c1e21 !important;
    letter-spacing: -0.025em;
    margin-bottom: 0 !important;
}
/* caption below title */
[data-testid="stCaptionContainer"] p {
    color: #606770 !important;
    font-size: 0.9rem !important;
    margin-top: 0.2rem;
}

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #dddfe2 !important;
}
[data-testid="stSidebar"] .stMarkdown p {
    color: #1c1e21;
    font-size: 0.85rem;
}
[data-testid="stSidebar"] strong {
    color: #1c1e21;
    font-weight: 600;
}
.sidebar-logo {
    font-family: 'Segoe UI', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    color: #1877F2;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 0 1.5rem;
    border-bottom: 1px solid #dddfe2;
    margin-bottom: 1rem;
}
.sidebar-logo .logo-mark {
    width: 28px;
    height: 28px;
}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 1px solid #dddfe2 !important;
    margin-bottom: 1.5rem;
    gap: 1rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #606770 !important;
    font-family: 'Roboto', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    padding: 0.75rem 0.5rem !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    color: #1877F2 !important;
}
.stTabs [data-baseweb="tab-highlight"] { background-color: #1877F2 !important; height: 3px !important; }

/* ---- Expander (User Cards) ---- */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #dddfe2 !important;
    border-radius: 8px !important;
    margin-bottom: 0.75rem !important;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    padding: 1rem 1.25rem !important;
    font-family: 'Roboto', sans-serif;
    font-weight: 500;
    font-size: 0.95rem;
    color: #1c1e21 !important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    padding: 0 1.25rem 1.25rem !important;
    background: #FFFFFF;
}
[data-testid="stExpander"] p {
    color: #606770;
    font-size: 0.9rem;
}
[data-testid="stExpander"] strong {
    color: #1c1e21;
}

/* ---- Metrics ---- */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #dddfe2;
    border-radius: 8px;
    padding: 1.2rem 1.5rem !important;
}
[data-testid="stMetricLabel"] p {
    color: #606770 !important;
    font-size: 0.75rem !important;
    font-weight: 500;
    text-transform: uppercase;
}
[data-testid="stMetricValue"] {
    font-family: 'Segoe UI', sans-serif;
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #1877F2 !important;
}

/* ---- Buttons ---- */
.stButton > button {
    background: #E4E6EB !important;
    color: #1c1e21 !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Roboto', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.6rem 1.2rem !important;
    transition: background-color 0.2s !important;
}
.stButton > button:hover {
    background: #d8dbdf !important;

    color: white !important;
    border-color: transparent !important;}

/* Primary action buttons (logout, form submit) */
[data-testid="stFormSubmitButton"] > button,
.stButton > button:has(div:contains("Cerrar sesión")) {
    background: #1877F2 !important;
    color: white !important;
}
[data-testid="stFormSubmitButton"] > button:hover,
.stButton > button:has(div:contains("Cerrar sesión")):hover {
    background: #166FE5 !important;
}

/* Danger button (delete) */
.stButton > button:has(div:contains("🗑️")) {
    background: #fae0e0 !important;
    color: #dd3c10 !important;
}
.stButton > button:has(div:contains("🗑️")):hover {
    background: #f5c0c0 !important;
}

/* ---- Inputs y Forms ---- */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div > div {
    background: #FFFFFF !important;
    border: 1px solid #ccd0d5 !important;
    border-radius: 6px !important;
    color: #1c1e21 !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: #1877F2 !important;
    box-shadow: 0 0 0 2px #e7f3ff !important;
}
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label {
    color: #606770 !important;
    font-size: 0.8rem !important;
    font-weight: 500;
}

/* ---- Alerts ---- */
.stSuccess {
    background: #ECFDF5 !important;
    border-color: #A7F3D0 !important;
    color: #065F46 !important;
}
.stError {
    background: #fae0e0 !important;
    border-color: #f5c0c0 !important;
    color: #dd3c10 !important;
}
.stInfo {
    background: #e7f3ff !important;
    border-color: #bde4ff !important;
    color: #1877F2 !important;
}

hr {
    border: none;
    border-top: 1px solid #dddfe2 !important;
    margin: 1.5rem 0 !important;
}

/* Fix white texts */
label p, [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] {
    color: #1c1e21 !important;
}

/* Fix all input text colors */
div[data-testid="stTextInput"] input, 
div[data-baseweb="input"] input, 
.stTextInput input,
input[type="text"],
input[type="password"],
input[type="number"],
input[type="email"] {
    color: #1c1e21 !important;
    -webkit-text-fill-color: #1c1e21 !important;
    background-color: #FFFFFF !important;
}
</style>
"""


def admin_dashboard():
    require_admin()

    # Inject custom styles
    st.markdown(ADMIN_DASHBOARD_CSS, unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────────
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("Panel de Administración")
        st.caption("Gestión de usuarios y configuración del sistema")
    with col2:
        st.markdown('<div style="padding-top: 1rem;">', unsafe_allow_html=True)
        if st.button("Cerrar sesión", use_container_width=True):
            logout()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <img src="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png" class="logo-mark" alt="Logo">
            Ads Intelligence
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**Admin:** {st.session_state.get('admin_email', '')}")
        st.markdown("---")
        if st.button("Cerrar sesión", use_container_width=True, key="sidebar_logout"):
            logout()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["👥 Usuarios", "➕ Crear Usuario", "📊 Estadísticas"])

    # ── Tab 1: Users ──────────────────────────────────────────────────────────
    with tab1:
        st.subheader("Usuarios Registrados")

        users = get_all_users()
        if users:
            for user in users:
                with st.expander(f"📧 {user['email']} — {user['company_name']}"):
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

                    st.markdown('---')
                    st.markdown('#### Cambiar Plan')
                    with st.form(f"update_plan_form_{user['id']}"):
                        new_plan = st.selectbox(
                            "Seleccionar nuevo plan",
                            ["basic", "pro", "enterprise"],
                            index=["basic", "pro", "enterprise"].index(user['plan'])
                            if user['plan'] in ["basic", "pro", "enterprise"] else 0,
                            key=f"plan_{user['id']}",
                        )
                        if st.form_submit_button("Actualizar Plan"):
                            update_user_plan(user['id'], new_plan)
                            st.success(f"Plan actualizado a {new_plan}")
                            st.rerun()

                    st.markdown('---')
                    st.markdown('#### Configurar credenciales Facebook')
                    with st.form(f"save_credentials_form_{user['id']}"):
                        fb_app_id = st.text_input("App ID", key=f"app_{user['id']}")
                        fb_token = st.text_input("Access Token", type="password", key=f"token_{user['id']}")
                        fb_account = st.text_input("Account ID (act_...)", key=f"acc_{user['id']}")
                        if st.form_submit_button("💾 Guardar credenciales"):
                            update_user_credentials(user['id'], fb_app_id, fb_token, fb_account)
                            st.success("Credenciales guardadas")
        else:
            st.info("No hay usuarios registrados")

    # ── Tab 2: Create User ────────────────────────────────────────────────────
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

    # ── Tab 3: Stats ──────────────────────────────────────────────────────────
    with tab3:
        st.subheader("Estadísticas del Sistema")

        users = get_all_users()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Usuarios", len(users))
        with col2:
            st.metric("Usuarios Activos", sum(1 for u in users if u['is_active']))

        st.markdown("---")
        st.subheader("📋 Últimos Accesos")

        logs = get_recent_logs(limit=10)
        if logs:
            for log in logs:
                st.caption(f"🕐 {log['timestamp']} — {log['email']} — {log['action']}")
        else:
            st.info("No hay registros de acceso")