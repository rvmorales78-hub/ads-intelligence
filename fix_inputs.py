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
    color: #1c1e21 !important;
    -webkit-text-fill-color: #1c1e21 !important;
    background-color: #FFFFFF !important;
}
"""

files = glob.glob("*.py")
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if "/* Fix all input text colors */" not in content and "</style>" in content:
            content = content.replace("</style>", css_to_add + "</style>", 1)
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Fixed inputs in {f}")
    except FileNotFoundError:
        pass
