import glob

css_to_add = """
/* Fix white texts */
label p, [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] {
    color: #0F172A !important;
}
"""

files = ['client_dashboard.py', 'admin_dashboard.py', 'auth.py', 'landing.py', 'app.py']
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if "/* Fix white texts */" not in content and "
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

</style>" in content:
            # insert before </style>
            content = content.replace("</style>", css_to_add + "</style>", 1)
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Fixed {f}")
    except FileNotFoundError:
        pass
