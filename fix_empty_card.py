with open("auth.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("st.markdown('<div class=\"auth-card\">', unsafe_allow_html=True)", "")
content = content.replace("st.markdown('</div>', unsafe_allow_html=True)", "")

with open("auth.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Empty cards removed from auth.py")