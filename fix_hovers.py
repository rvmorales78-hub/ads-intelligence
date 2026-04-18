import glob
import re

files = glob.glob("*.py")
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    modified = False
    
    # Use regex to find button hover selectors and inject color: white !important
    new_content = re.sub(
        r'(\.stButton > button:hover[^\{]*\{)([^\
    color: white !important;
    border-color: transparent !important;}]*)',
        lambda m: m.group(1) + m.group(2) + ("" if "color:" in m.group(2) else "\n    color: white !important;\n    border-color: transparent !important;"),
        content
    )
    
    new_content = re.sub(
        r'(\.stFormSubmitButton > button:hover[^\{]*\{)([^\
    color: white !important;
    border-color: transparent !important;}]*)',
        lambda m: m.group(1) + m.group(2) + ("" if "color:" in m.group(2) else "\n    color: white !important;\n    border-color: transparent !important;"),
        new_content
    )
    
    new_content = re.sub(
        r'(\[data-testid=[\'"]stBaseButton-primary[\'"]\]:hover[^\{]*\{)([^\}]*)',
        lambda m: m.group(1) + m.group(2) + ("" if "color:" in m.group(2) else "\n    color: white !important;\n    border-color: transparent !important;"),
        new_content
    )
    
    if new_content != content:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Hovers fixed in {f}")

print("Done.")