import streamlit as st
print('>>> auth.py cargado')
from database import verify_user, verify_admin, log_access, get_user_credentials, create_user, get_user_with_trial_info, create_password_reset_token, verify_and_reset_password
print('>>> importaciones desde database.py realizadas, incluyendo create_user y get_user_with_trial_info')
import hashlib

AUTH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
body, .stApp { background: #F1F5F9 !important; color: #0F172A; font-family: 'Roboto', sans-serif; }
h1,h2,h3 { color: #0F172A !important; font-family: 'Segoe UI', 'Roboto', sans-serif; font-weight: 700; }

/* ---- CENTRADO ---- */
.block-container { max-width: 420px !important; margin: 0 auto !important; padding-top: 4rem !important; }

/* ---- LOGO ---- */
.auth-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
    font-family: 'Segoe UI', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 2.5rem;
    text-align: center;
}
.auth-logo-mark {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    object-fit: contain;
}

/* ---- CARD ---- */
.auth-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, .1), 0 8px 16px rgba(0, 0, 0, .1);
}
.auth-card-title {
    font-family: 'Segoe UI', sans-serif;
    font-size: 1.3rem;
    font-weight: 600;
    text-align: center;
    color: #0F172A;
    margin-bottom: 0.3rem;
}
.auth-card-sub {
    font-size: 0.9rem;
    color: #475569;
    margin-bottom: 1.5rem;
    text-align: center;
}
.auth-divider { border: none; border-top: 1px solid #E2E8F0; margin: 1.5rem 0; }

/* ---- TABS ---- */
.stTabs [data-baseweb="tab-list"] {
    justify-content: center;
    border-bottom: 1px solid #E2E8F0 !important;
    margin-bottom: 1.5rem;
    gap: 1rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #475569 !important;
    font-family: 'Roboto', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    padding: 0.75rem 0.5rem !important;
    border: none !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    color: #0F172A !important;
}
.stTabs [data-baseweb="tab-highlight"] { background-color: #0F172A !important; height: 3px !important; }
.stTabs [data-baseweb="tab-border"]    { display: none !important; }

/* ---- INPUTS ---- */
.stTextInput label {
    display: none !important;
}
.stTextInput input {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
    color: #0F172A !important;
    font-family: 'Roboto', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.8rem 1rem !important;
    transition: border-color 0.2s !important;
    margin-bottom: 0.5rem; /* Space between inputs */
}
.stTextInput input:focus {
    border-color: #0F172A !important;
    box-shadow: 0 0 0 2px #F8FAFC !important;
}
.stTextInput input::placeholder { color: #64748B !important; }

/* ---- SUBMIT BUTTON ---- */
.stFormSubmitButton > button, .stButton > button, [data-testid='stFormSubmitButton'] > button, [data-testid='stBaseButton-primary'] {
    background: #0F172A !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Roboto', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    padding: 0.7rem 2rem !important;
    width: 100% !important;
    margin-top: 0.5rem !important;
    transition: background-color 0.2s !important;
}
.stFormSubmitButton > button:hover, .stButton > button:hover, [data-testid='stFormSubmitButton'] > button:hover, [data-testid='stBaseButton-primary']:hover {
    background: #1E293B !important;

    color: white !important;
    border-color: transparent !important;}

/* ---- MESSAGES ---- */
.stAlert {
    background: #FFFFFF !important;
    border: 1px solid #DC2626 !important;
    border-radius: 6px !important;
    color: #DC2626 !important;
    font-size: 0.85rem !important;
}
[data-baseweb="notification"] { border-radius: 6px !important; }

/* ---- FOOTER ---- */
.auth-footer {
    text-align: center;
    font-size: 0.75rem;
    color: #64748B;
    margin-top: 2rem;
    padding-bottom: 2rem;
}

/* Fix white texts */
label p, [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] {
    color: #0F172A !important;
}

/* Fix all input text colors */
div[data-testid="stTextInput"] input, 
div[data-baseweb="input"] input, 
.stTextInput input,
input[type="text"],
input[type="password"],
input[type="number"],
input[type="email"] {
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    background-color: #FFFFFF !important;
}

/* ---- ALERTS OVERRIDES ---- */
div[data-testid="stAlert"] {
    background-color: #FFFFFF !important;
    border-radius: 8px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}
div[data-testid="stAlert"] p { color: #0F172A !important; }
div[data-testid="stNotification"] { background-color: #FFFFFF !important; }

/* Let Streamlit's native icon colors work, but force the background to white. */

</style>
"""


def login_page():
    """Pantalla de login con diseño premium dark luxury"""


    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    # ---- CARD WRAPPER ----
    

    # ---- LOGO ----
    st.markdown("""
    <div class="auth-logo" style="margin-bottom: 1.5rem; margin-top: 0.5rem;">
        <img src="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png" class="auth-logo-mark" alt="Logo">
        Ads Intelligence
    </div>
    """, unsafe_allow_html=True)

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

                    # Obtener la fecha de inicio de la prueba (created_at)
                    user_full_info = get_user_with_trial_info(st.session_state['user_id'])
                    st.session_state['trial_start_date'] = user_full_info['created_at'] # Usamos created_at como trial_start_date

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
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("¿Olvidaste tu contraseña?", key="forgot_pass_client", use_container_width=True):
            st.session_state.page = 'forgot_password'
            st.rerun()

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

    

    # ---- FOOTER ----
    st.markdown("""
    <div class="auth-footer">
        © 2026 Ads Intelligence · Todos los derechos reservados
    </div>
    """, unsafe_allow_html=True)


def register_page():
    """Pantalla de registro de usuario con diseño premium dark luxury"""
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    # ---- CARD WRAPPER ----
    

    # ---- LOGO ----
    st.markdown("""
    <div class="auth-logo" style="margin-bottom: 1.5rem; margin-top: 0.5rem;">
        <img src="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png" class="auth-logo-mark" alt="Logo">
        Ads Intelligence
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-card-title">Crea tu cuenta</div>
    <div class="auth-card-sub">Empieza con nuestro plan gratuito para siempre.<br>
    <span style="font-size: 0.75rem; color: rgba(201,168,76,0.8);">*Si tienes varias campañas, analizaremos la de mayor inversión.</span></div>
    """, unsafe_allow_html=True)

    with st.form("register_form"):
        email = st.text_input("Email", placeholder="tu@empresa.com", key="register_email")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••", key="register_pass")
        company_name = st.text_input("Nombre de la empresa", placeholder="Tu Empresa S.L.", key="register_company")
        
        submitted = st.form_submit_button("Crear cuenta gratis →", use_container_width=True)

        if submitted:
            if not email or not password or not company_name:
                st.error("Por favor, completa todos los campos.")
            elif create_user(email, password, company_name, plan='basic'):
                st.success("✅ Cuenta creada exitosamente. ¡Bienvenido! Tu plan analizará automáticamente la campaña de mayor inversión.")
                # Redirigir al login para que el usuario inicie sesión con su nueva cuenta
                st.session_state.page = 'login'
                st.rerun()
            else:
                st.error("❌ El email ya está registrado o hubo un error al crear la cuenta.")

    

    # ---- FOOTER ----
    st.markdown("""
    <div class="auth-footer">
        © 2026 Ads Intelligence · Todos los derechos reservados
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin-top:1.5rem; font-size:0.85rem; color:#64748B;">
        ¿Ya tienes una cuenta?
    </div>
    """, unsafe_allow_html=True)
    # Usamos un botón de Streamlit para la navegación, que es más robusto que el JavaScript en markdown.
    if st.button("Inicia sesión aquí", key="go_to_login_from_register", use_container_width=True):
        st.session_state.page = 'login'
        st.rerun()
    # Ocultamos el botón si no queremos que se vea, pero la funcionalidad de navegación es clave.
    # st.markdown(
    #     """<style>button[data-testid="stButton"] {display: none;} </style>""",
    #     unsafe_allow_html=True,
    # )


def forgot_password_page():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="auth-logo" style="margin-bottom: 1.5rem; margin-top: 0.5rem;">
        <img src="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png" class="auth-logo-mark" alt="Logo">
        Ads Intelligence
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-card-title">Recuperar Contraseña</div>
    <div class="auth-card-sub">Ingresa tu email y te enviaremos un enlace.</div>
    """, unsafe_allow_html=True)

    with st.form("forgot_pass_form"):
        email = st.text_input("Email", placeholder="tu@empresa.com")
        submitted = st.form_submit_button("Enviar enlace de recuperación →", use_container_width=True)

        if submitted:
            if not email:
                st.error("Por favor, ingresa tu email.")
            else:
                token = create_password_reset_token(email)
                if token:
                    # In a real app we would send an email here.
                    # For this prototype we will show a success message with the link to click.
                    reset_link = f"/?page=reset_password&token={token}"
                    st.success(f"Enlace de recuperación generado.")
                    st.markdown(f"""
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:1rem; border-radius:8px; text-align:center; margin-top:1rem;">
                        <span style="font-size:0.85rem; color:#475569;">Simulación de Email enviado. En producción esto iría a tu correo.</span><br>
                        <a href="{reset_link}" target="_self" style="color:#0F172A; font-weight:700; text-decoration:none; display:inline-block; margin-top:0.5rem;">Haz clic aquí para restablecer tu contraseña</a>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # We shouldn't reveal if email exists, but for UX here we can say email sent anyway
                    st.success("Si el email existe en nuestro sistema, hemos enviado un enlace de recuperación.")

    if st.button("← Volver al login", use_container_width=True):
        st.session_state.page = 'login'
        st.rerun()

def reset_password_page():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="auth-logo" style="margin-bottom: 1.5rem; margin-top: 0.5rem;">
        <img src="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png" class="auth-logo-mark" alt="Logo">
        Ads Intelligence
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-card-title">Restablecer Contraseña</div>
    <div class="auth-card-sub">Ingresa tu nueva contraseña.</div>
    """, unsafe_allow_html=True)

    token = st.session_state.get('reset_token', None)
    
    if not token:
        st.error("Token de recuperación inválido o ausente.")
        if st.button("← Ir al login", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()
        return

    with st.form("reset_pass_form"):
        password = st.text_input("Nueva contraseña", type="password", placeholder="••••••••")
        confirm_password = st.text_input("Confirmar nueva contraseña", type="password", placeholder="••••••••")
        
        submitted = st.form_submit_button("Restablecer Contraseña →", use_container_width=True)

        if submitted:
            if not password or not confirm_password:
                st.error("Completa ambos campos.")
            elif password != confirm_password:
                st.error("Las contraseñas no coinciden.")
            elif len(password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
            else:
                if verify_and_reset_password(token, password):
                    st.success("✅ ¡Contraseña restablecida con éxito!")
                    # Borrar el token para que no se re-use si recarga
                    del st.session_state['reset_token']
                    st.markdown("""
                    <script>
                        setTimeout(function() {
                            window.location.href = "/?page=login";
                        }, 2000);
                    </script>
                    """, unsafe_allow_html=True)
                    st.info("Serás redirigido al login en 2 segundos...")
                else:
                    st.error("❌ El enlace es inválido o ha expirado.")

    if st.button("← Volver al login", use_container_width=True):
        st.session_state.page = 'login'
        st.rerun()

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
        <div style="background:#FFFFFF; border:1px solid #E2E8F0;
             border-radius:14px; padding:1.25rem; font-size:0.875rem; color:#DC2626; text-align:center;">
            <strong>Acceso denegado</strong><br>
            <span style="color:#94A3B8; font-size:0.8rem;">Se requieren privilegios de administrador.</span>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
        return False
    return True