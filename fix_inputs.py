import glob

css_to_add = """
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
"""

files = glob.glob("*.py")
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if "/* Fix all input text colors */" not in content and "
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

</style>" in content:
            content = content.replace("</style>", css_to_add + "</style>", 1)
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Fixed inputs in {f}")
    except FileNotFoundError:
        pass
