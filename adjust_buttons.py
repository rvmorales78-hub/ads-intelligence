import glob

files = glob.glob("*.py")
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Let's clean up any leftover rgba(255,255,255) that were used as borders or separators 
    content = content.replace("#E2E8F0", "#E2E8F0")
    content = content.replace("#E2E8F0", "#E2E8F0")
    content = content.replace("#F8FAFC", "#F8FAFC")
    content = content.replace("#F8FAFC", "#F8FAFC")
    content = content.replace("#F8FAFC", "#F8FAFC")
    content = content.replace("#F8FAFC", "#F8FAFC")
    content = content.replace("#E2E8F0", "#E2E8F0")
    content = content.replace("#E2E8F0", "#E2E8F0")
    
    # Same for black rgba if they are too light
    content = content.replace("#F8FAFC", "#F8FAFC")
    content = content.replace("#E2E8F0", "#E2E8F0")
    content = content.replace("#F8FAFC", "#F8FAFC")
    content = content.replace("#F8FAFC", "#F8FAFC")
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
print("Finished button adjustments")