def run():
    with open('auth.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update imports
    old_import = "from database import verify_user, verify_admin, log_access, get_user_credentials, create_user, get_user_with_trial_info"
    new_import = "from database import verify_user, verify_admin, log_access, get_user_credentials, create_user, get_user_with_trial_info, create_password_reset_token, verify_and_reset_password"
    content = content.replace(old_import, new_import)

    # 2. Update forgot password button click action
    old_button_action = 'st.info("Para recuperar tu contraseña, envíanos un correo a soporte@adsintelligence.com o contacta a tu administrador.")'
    new_button_action = "st.session_state.page = 'forgot_password'\n            st.rerun()"
    content = content.replace(old_button_action, new_button_action)

    # 3. Add forgot_password_page and reset_password_page
    new_pages = """
def forgot_password_page():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown(\"\"\"
    <div class="auth-logo" style="margin-bottom: 1.5rem; margin-top: 0.5rem;">
        <img src="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png" class="auth-logo-mark" alt="Logo">
        Ads Intelligence
    </div>
    \"\"\", unsafe_allow_html=True)

    st.markdown(\"\"\"
    <div class="auth-card-title">Recuperar Contraseña</div>
    <div class="auth-card-sub">Ingresa tu email y te enviaremos un enlace.</div>
    \"\"\", unsafe_allow_html=True)

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
                    st.markdown(f\"\"\"
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:1rem; border-radius:8px; text-align:center; margin-top:1rem;">
                        <span style="font-size:0.85rem; color:#475569;">Simulación de Email enviado. En producción esto iría a tu correo.</span><br>
                        <a href="{reset_link}" target="_self" style="color:#0F172A; font-weight:700; text-decoration:none; display:inline-block; margin-top:0.5rem;">Haz clic aquí para restablecer tu contraseña</a>
                    </div>
                    \"\"\", unsafe_allow_html=True)
                else:
                    # We shouldn't reveal if email exists, but for UX here we can say email sent anyway
                    st.success("Si el email existe en nuestro sistema, hemos enviado un enlace de recuperación.")

    if st.button("← Volver al login", use_container_width=True):
        st.session_state.page = 'login'
        st.rerun()

def reset_password_page():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown(\"\"\"
    <div class="auth-logo" style="margin-bottom: 1.5rem; margin-top: 0.5rem;">
        <img src="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png" class="auth-logo-mark" alt="Logo">
        Ads Intelligence
    </div>
    \"\"\", unsafe_allow_html=True)

    st.markdown(\"\"\"
    <div class="auth-card-title">Restablecer Contraseña</div>
    <div class="auth-card-sub">Ingresa tu nueva contraseña.</div>
    \"\"\", unsafe_allow_html=True)

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
                    st.markdown(\"\"\"
                    <script>
                        setTimeout(function() {
                            window.location.href = "/?page=login";
                        }, 2000);
                    </script>
                    \"\"\", unsafe_allow_html=True)
                    st.info("Serás redirigido al login en 2 segundos...")
                else:
                    st.error("❌ El enlace es inválido o ha expirado.")

    if st.button("← Volver al login", use_container_width=True):
        st.session_state.page = 'login'
        st.rerun()
"""

    if "def forgot_password_page():" not in content:
        # Append before logout() to keep it grouped with other auth pages
        content = content.replace("def logout():", new_pages + "\ndef logout():")

    with open('auth.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("auth.py updated with reset flow")

run()