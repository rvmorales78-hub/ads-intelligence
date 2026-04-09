import streamlit as st
from database import verify_user, verify_admin, log_access, get_user_credentials
import hashlib

AUTH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Outfit:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
body, .stApp { background: #080810 !important; color: #E8E6F0; font-family: 'Outfit', sans-serif; }
h1,h2,h3 { font-family: 'Syne', sans-serif; }

/* ---- CENTRADO ---- */
.block-container { max-width: 480px !important; margin: 0 auto !important; padding-top: 4rem !important; }

/* ---- LOGO ---- */
.auth-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    color: #F5F3FF;
    margin-bottom: 2.5rem;
    text-align: center;
}
.auth-logo-mark {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #C9A84C, #8A6AE0);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}

/* ---- CARD ---- */
.auth-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 24px;
    padding: 2.25rem 2rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.auth-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(201,168,76,0.35), transparent);
}
.auth-card-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    color: #F5F3FF;
    margin-bottom: 0.3rem;
}
.auth-card-sub {
    font-size: 0.82rem;
    color: rgba(232,230,240,0.35);
    margin-bottom: 1.75rem;
}
.auth-divider { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 1.5rem 0; }

/* ---- TABS ---- */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    margin-bottom: 1.5rem;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: rgba(232,230,240,0.4) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.25rem !important;
    border: none !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(138,106,224,0.18) !important;
    color: #A890F0 !important;
    border: 1px solid rgba(138,106,224,0.3) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"]    { display: none !important; }

/* ---- INPUTS ---- */
.stTextInput label {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: rgba(232,230,240,0.4) !important;
    margin-bottom: 0.3rem !important;
}
.stTextInput input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    color: #F5F3FF !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 1rem !important;
    transition: border-color 0.2s !important;
}
.stTextInput input:focus {
    border-color: rgba(138,106,224,0.5) !important;
    box-shadow: 0 0 0 3px rgba(138,106,224,0.08) !important;
}
.stTextInput input::placeholder { color: rgba(232,230,240,0.2) !important; }

/* ---- SUBMIT BUTTON ---- */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #8A6AE0 0%, #6A4AC0 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.7rem 2rem !important;
    width: 100% !important;
    margin-top: 0.5rem !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.2s, transform 0.15s !important;
}
.stFormSubmitButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ---- MESSAGES ---- */
.stAlert {
    background: rgba(252,129,129,0.07) !important;
    border: 1px solid rgba(252,129,129,0.2) !important;
    border-radius: 12px !important;
    color: #FC8181 !important;
    font-size: 0.85rem !important;
}
[data-baseweb="notification"] { border-radius: 12px !important; }

/* ---- FOOTER ---- */
.auth-footer {
    text-align: center;
    font-size: 0.75rem;
    color: rgba(232,230,240,0.2);
    margin-top: 2rem;
    padding-bottom: 2rem;
}
</style>
"""


def login_page():
    """Pantalla de login con diseño premium dark luxury"""

    st.set_page_config(
        page_title="Ads Intelligence — Acceso",
        page_icon="◈",
        layout="centered"
    )

    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    # ---- LOGO ----
    st.markdown("""
    <div class="auth-logo">
        <div class="auth-logo-mark">◈</div>
        Ads Intelligence
    </div>
    """, unsafe_allow_html=True)

    # ---- CARD WRAPPER ----
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)

    # Tabs
    tab1, tab2 = st.tabs(["Cliente", "Administrador"])

    # ---- TAB CLIENTE ----
    with tab1:
        st.markdown("""
        <div class="auth-card-title">Bienvenido de vuelta</div>
        <div class="auth-card-sub">Accede a tu panel de campañas</div>
        """, unsafe_allow_html=True)

        with st.form("login_client"):
            st.text_input("Email", placeholder="tu@empresa.com", key="client_email")
            st.text_input("Contraseña", type="password", placeholder="••••••••", key="client_pass")
            submitted = st.form_submit_button("Ingresar →", use_container_width=True)

            if submitted:
                user = verify_user(
                    st.session_state.get("client_email", ""),
                    st.session_state.get("client_pass", "")
                )
                if user:
                    st.session_state['authenticated'] = True
                    st.session_state['user_id']       = int(user['id'])
                    st.session_state['user_email']    = str(user['email'] or '')
                    st.session_state['user_type']     = 'client'
                    st.session_state['company_name']  = str(user.get('company_name') or '')
                    st.session_state['plan']          = str(user.get('plan') or 'basic')

                    st.session_state['fb_app_id_enc']  = str(user.get('fb_app_id') or '')
                    st.session_state['fb_token_enc']   = str(user.get('fb_access_token') or '')
                    st.session_state['fb_account_enc'] = str(user.get('fb_account_id') or '')

                    st.session_state['fb_configured'] = bool(
                        st.session_state['fb_app_id_enc'] and
                        st.session_state['fb_token_enc'] and
                        st.session_state['fb_account_enc']
                    )

                    log_access(int(user['id']), 'login', 'unknown')
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("Email o contraseña incorrectos")

    # ---- TAB ADMIN ----
    with tab2:
        st.markdown("""
        <div class="auth-card-title">Panel de administración</div>
        <div class="auth-card-sub">Acceso restringido a administradores</div>
        """, unsafe_allow_html=True)

        with st.form("login_admin"):
            st.text_input("Email",      placeholder="admin@empresa.com", key="admin_email_input")
            st.text_input("Contraseña", type="password", placeholder="••••••••", key="admin_pass")
            submitted = st.form_submit_button("Ingresar como Admin →", use_container_width=True)

            if submitted:
                admin = verify_admin(
                    st.session_state.get("admin_email_input", ""),
                    st.session_state.get("admin_pass", "")
                )
                if admin:
                    st.session_state['authenticated'] = True
                    st.session_state['user_type']     = 'admin'
                    st.session_state['admin_email']   = st.session_state.get("admin_email_input", "")
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("Credenciales de administrador incorrectas")

    st.markdown('</div>', unsafe_allow_html=True)

    # ---- FOOTER ----
    st.markdown("""
    <div class="auth-footer">
        © 2024 Ads Intelligence · Todos los derechos reservados
    </div>
    """, unsafe_allow_html=True)


def logout():
    """Cierra sesión y redirige al landing"""
    keys = [
        'authenticated', 'user_id', 'user_email', 'user_type',
        'company_name', 'plan', 'fb_app_id', 'fb_access_token',
        'fb_account_id', 'fb_configured', 'admin_email', 'page'
    ]
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.page = 'landing'
    st.rerun()


def require_auth():
    """Verifica autenticación activa"""
    if 'authenticated' not in st.session_state:
        st.session_state.page = 'login'
        st.rerun()
        st.stop()
        return False
    return True


def require_admin():
    """Verifica privilegios de administrador"""
    if not require_auth():
        return False
    if st.session_state.get('user_type') != 'admin':
        st.markdown("""
        <div style="background:rgba(252,129,129,0.07); border:1px solid rgba(252,129,129,0.2);
             border-radius:14px; padding:1.25rem; font-size:0.875rem; color:#FC8181; text-align:center;">
            <strong>Acceso denegado</strong><br>
            <span style="color:rgba(232,230,240,0.4); font-size:0.8rem;">Se requieren privilegios de administrador.</span>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
        return False
    return True