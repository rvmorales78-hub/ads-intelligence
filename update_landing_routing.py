def run():
    with open('landing.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_routing_1 = "if page_to_go in ['login', 'register', 'demo', 'landing', 'strategy']:"
    new_routing_1 = """if page_to_go in ['login', 'register', 'demo', 'landing', 'strategy', 'forgot_password', 'reset_password']:
        if page_to_go == 'reset_password' and "token" in query_params:
            st.session_state.reset_token = query_params["token"]"""
    
    content = content.replace(old_routing_1, new_routing_1)
    
    old_routing_2 = """if st.session_state.page == 'register': # Nueva página de registro
    register_page()
    st.stop()"""
    new_routing_2 = """if st.session_state.page == 'register': # Nueva página de registro
    register_page()
    st.stop()

if st.session_state.page == 'forgot_password':
    from auth import forgot_password_page
    forgot_password_page()
    st.stop()

if st.session_state.page == 'reset_password':
    from auth import reset_password_page
    reset_password_page()
    st.stop()"""
    
    content = content.replace(old_routing_2, new_routing_2)
    
    with open('landing.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("landing.py updated")

run()