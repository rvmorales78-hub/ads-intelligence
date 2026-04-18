import re

with open("auth.py", "r", encoding="utf-8") as f:
    text = f.read()

# Login Page Replacements
old_login_logo = """    # ---- LOGO ----
    st.markdown(\"\"\"
    <div class="auth-logo">
        <img src="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png" class="auth-logo-mark" alt="Logo">
        Ads Intelligence
    </div>
    \"\"\", unsafe_allow_html=True)

    # ---- CARD WRAPPER ----
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)"""

new_login_logo = """    # ---- CARD WRAPPER ----
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)

    # ---- LOGO ----
    st.markdown(\"\"\"
    <div class="auth-logo" style="margin-bottom: 1.5rem; margin-top: 0.5rem;">
        <img src="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png" class="auth-logo-mark" alt="Logo">
        Ads Intelligence
    </div>
    \"\"\", unsafe_allow_html=True)"""

text = text.replace(old_login_logo, new_login_logo)

# Register Page Replacements
old_register_logo = """    # ---- LOGO ----
    st.markdown(\"\"\"
    <div class="auth-logo">
        <img src="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png" class="auth-logo-mark" alt="Logo">
        Ads Intelligence
    </div>
    \"\"\", unsafe_allow_html=True)

    # ---- CARD WRAPPER ----
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)"""

text = text.replace(old_register_logo, new_login_logo)


# Add forgotten password below client submit button handling
old_client_submit = """                    log_access(int(user['id']), 'login', 'unknown')
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("Email o contraseña incorrectos")"""

new_client_submit = """                    log_access(int(user['id']), 'login', 'unknown')
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("Email o contraseña incorrectos")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("¿Olvidaste tu contraseña?", key="forgot_pass_client", use_container_width=True):
            st.info("Para recuperar tu contraseña, envíanos un correo a soporte@adsintelligence.com o contacta a tu administrador.")"""

text = text.replace(old_client_submit, new_client_submit)

with open("auth.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Auth modified.")