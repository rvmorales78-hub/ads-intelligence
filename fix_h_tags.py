import glob
import re

files = glob.glob("*.py")
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if "h1,h2,h3" in content:
        content = content.replace("h1,h2,h3 { color: #0F172A !important; font-family", "h1,h2,h3 { color: #0F172A !important; font-family")
        content = content.replace("h1,h2,h3,h4 { color: #0F172A !important; font-family", "h1,h2,h3,h4 { color: #0F172A !important; font-family")
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

print("H tags fixed.")