import glob

css_to_add = """
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
"""

files = glob.glob("*.py")
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if "/* ---- ALERTS OVERRIDES ---- */" not in content and "</style>" in content:
            content = content.replace("</style>", css_to_add + "\n</style>", 1)
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Fixed alerts in {f}")
    except FileNotFoundError:
        pass