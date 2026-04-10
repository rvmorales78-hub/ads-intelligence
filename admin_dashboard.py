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


CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

/* ── Base & Reset ───────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #080c14;
    color: #c9d1e0;
}

/* ── Hide default Streamlit chrome ──────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2.5rem 3rem 4rem;
    max-width: 1100px;
}

/* ── Sidebar ─────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0d1220 !important;
    border-right: 1px solid #1e2a3a;
}
[data-testid="stSidebar"] .stMarkdown p {
    color: #7a8fa8;
    font-size: 0.85rem;
}
[data-testid="stSidebar"] strong {
    color: #e0e8f5;
    font-weight: 600;
}

/* ── Title ───────────────────────────────────── */
h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: #e8eef8 !important;
    letter-spacing: -0.03em;
    line-height: 1.15 !important;
    margin-bottom: 0 !important;
}

/* caption below title */
[data-testid="stCaptionContainer"] p {
    color: #4a5f7a !important;
    font-size: 0.82rem !important;
    margin-top: 0.2rem;
    letter-spacing: 0.02em;
}

/* ── Subheadings ─────────────────────────────── */
h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #c4d0e8 !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}
h4 {
    font-family: 'DM Sans', sans-serif !important;
    color: #7a94b8 !important;
    font-weight: 500 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.6rem !important;
}

/* ── Tabs ────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    background: #0d1220;
    border: 1px solid #1a2535;
    border-radius: 12px;
    padding: 4px;
    gap: 2px;
    margin-bottom: 1.5rem;
}
[data-testid="stTabs"] [role="tab"] {
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.85rem;
    color: #4a5f7a !important;
    padding: 0.5rem 1.1rem !important;
    border: none !important;
    transition: all 0.2s ease;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: #162035 !important;
    color: #7eb8f5 !important;
    box-shadow: 0 0 0 1px #2a3f5a;
}
[data-testid="stTabs"] [role="tab"]:hover:not([aria-selected="true"]) {
    color: #8aa3c0 !important;
    background: #111927 !important;
}
/* hide the default bottom indicator line */
[data-testid="stTabs"] [role="tablist"]::after,
[data-testid="stTabs"] [role="tab"]::after { display: none !important; }

/* ── Expander (User Cards) ───────────────────── */
[data-testid="stExpander"] {
    background: #0d1220 !important;
    border: 1px solid #1a2535 !important;
    border-radius: 14px !important;
    margin-bottom: 0.75rem !important;
    overflow: hidden;
    transition: border-color 0.2s ease;
}
[data-testid="stExpander"]:hover {
    border-color: #2a3f5a !important;
}
[data-testid="stExpander"] summary {
    padding: 1rem 1.25rem !important;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.9rem;
    color: #a8bcd8 !important;
}
[data-testid="stExpander"] summary:hover {
    background: #111927 !important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    padding: 0 1.25rem 1.25rem !important;
}

/* ── Write / p text inside cards ─────────────── */
[data-testid="stExpander"] p {
    color: #6a82a0;
    font-size: 0.86rem;
    margin: 0.25rem 0;
}
[data-testid="stExpander"] strong {
    color: #99b3d0;
}

/* ── Divider ─────────────────────────────────── */
hr {
    border: none;
    border-top: 1px solid #1a2535 !important;
    margin: 1rem 0 !important;
}

/* ── Metrics ─────────────────────────────────── */
[data-testid="stMetric"] {
    background: #0d1220;
    border: 1px solid #1a2535;
    border-radius: 14px;
    padding: 1.2rem 1.5rem !important;
    transition: border-color 0.2s;
}
[data-testid="stMetric"]:hover { border-color: #2a4060; }
[data-testid="stMetricLabel"] p {
    color: #4a6080 !important;
    font-size: 0.75rem !important;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    color: #7eb8f5 !important;
}

/* ── Buttons ─────────────────────────────────── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.83rem !important;
    border-radius: 9px !important;
    border: 1px solid #1e2f45 !important;
    background: #111927 !important;
    color: #7a9ab8 !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: #162035 !important;
    border-color: #2a4060 !important;
    color: #a8c8f0 !important;
    transform: translateY(-1px);
}
/* Danger-style delete buttons */
button[kind="secondary"]:has(div:contains("🗑️")),
.stButton > button:has(div:contains("Eliminar")) {
    border-color: #3a1a1a !important;
    color: #c06060 !important;
}
.stButton > button:has(div:contains("Eliminar")):hover {
    background: #1e0f0f !important;
    border-color: #5a2020 !important;
    color: #e08080 !important;
}

/* ── Form submit buttons ─────────────────────── */
[data-testid="stFormSubmitButton"] > button {
    background: #132540 !important;
    border-color: #1e3d62 !important;
    color: #7eb8f5 !important;
    font-weight: 600 !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    background: #1a3254 !important;
    border-color: #2a5080 !important;
    color: #a8d0f8 !important;
}

/* ── Inputs ──────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div > div {
    background: #0a1020 !important;
    border: 1px solid #1a2840 !important;
    border-radius: 9px !important;
    color: #a8bcd8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.87rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #2a5080 !important;
    box-shadow: 0 0 0 2px rgba(46, 100, 160, 0.2) !important;
}
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label {
    color: #4a6080 !important;
    font-size: 0.78rem !important;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Selectbox dropdown ──────────────────────── */
[data-testid="stSelectbox"] svg { color: #4a6080 !important; }

/* ── Alerts / Info ───────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.85rem;
    font-family: 'DM Sans', sans-serif;
}

/* ── Success / Error messages ────────────────── */
.stSuccess {
    background: #0a1e14 !important;
    border-color: #1a4030 !important;
    color: #5ab888 !important;
    border-radius: 10px !important;
}
.stError {
    background: #1a0a0a !important;
    border-color: #4a1818 !important;
    color: #e07070 !important;
    border-radius: 10px !important;
}

/* ── Log captions ────────────────────────────── */
[data-testid="stCaptionContainer"] {
    background: #0d1220;
    border: 1px solid #161f2e;
    border-radius: 8px;
    padding: 0.5rem 0.9rem !important;
    margin-bottom: 0.35rem !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #4a6080 !important;
    font-size: 0.78rem !important;
}

/* ── Scrollbar ───────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #080c14; }
::-webkit-scrollbar-thumb { background: #1e2f45; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2a4060; }

/* ── Column gaps ─────────────────────────────── */
[data-testid="column"] { gap: 0.75rem; }
</style>
"""


def admin_dashboard():
    require_admin()

    # Inject custom styles
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────────
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("👑 Panel de Administración")
        st.caption("Gestión de usuarios y configuración del sistema")
    with col2:
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            logout()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"**Admin:** {st.session_state.get('admin_email', '')}")
        st.markdown("---")
        if st.button("🚪 Cerrar sesión", use_container_width=True, key="sidebar_logout"):
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
        st.metric("Total Usuarios", len(users))
        st.metric("Usuarios Activos", sum(1 for u in users if u['is_active']))

        st.markdown("---")
        st.subheader("📋 Últimos Accesos")

        logs = get_recent_logs(limit=10)
        if logs:
            for log in logs:
                st.caption(f"🕐 {log['timestamp']} — {log['email']} — {log['action']}")
        else:
            st.info("No hay registros de acceso")