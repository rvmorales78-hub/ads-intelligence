import glob

replacements = {
    # Blues
    '#0F172A': '#0F172A', # Primary Slate 900
    '#1E293B': '#1E293B', # Hover Slate 800
    '#F8FAFC': '#F8FAFC', # Light bg -> Slate 50
    '#E2E8F0': '#E2E8F0', # Borders -> Slate 200
    
    # Greens -> Emerald
    '#059669': '#059669',
    '#059669': '#059669',
    '#064E3B': '#064E3B',
    '#FFFFFF': '#FFFFFF', # Remove colored bg
    '#E2E8F0': '#E2E8F0', # Border

    # Reds -> Red
    '#DC2626': '#DC2626',
    '#DC2626': '#DC2626',
    '#FFFFFF': '#FFFFFF', # Remove colored bg
    '#E2E8F0': '#E2E8F0', # Border

    # Yellows -> Amber
    '#D97706': '#D97706',
    '#D97706': '#D97706',
    '#B45309': '#B45309',
    '#FFFFFF': '#FFFFFF', # Remove colored bg
    '#E2E8F0': '#E2E8F0', # Border

    # Purples -> Slate/Indigo
    '#4F46E5': '#4F46E5',
    '#6366F1': '#6366F1',
    '#0F172A': '#0F172A',

    # Backgrounds and Grays
    '#F1F5F9': '#F1F5F9', # Main Background (Slate 100)
    '#0F172A': '#0F172A', # Main Text (Slate 900)
    '#475569': '#475569', # Muted Text (Slate 600)
    '#64748B': '#64748B', # Light Text (Slate 500)
    '#CBD5E1': '#CBD5E1', # Borders (Slate 300)
    '#E2E8F0': '#E2E8F0', # Light Borders (Slate 200)

    # Inline RGBA backgrounds
    '#FFFFFF': '#FFFFFF',
    '#E2E8F0': '#E2E8F0',
    '#FFFFFF': '#FFFFFF',
    '#F8FAFC': '#F8FAFC',
    
    '#FFFFFF': '#FFFFFF',
    '#E2E8F0': '#E2E8F0',
    '#FFFFFF': '#FFFFFF',
    '#F8FAFC': '#F8FAFC',
    
    '#FFFFFF': '#FFFFFF',
    '#E2E8F0': '#E2E8F0',
    '#FFFFFF': '#FFFFFF',
    '#F8FAFC': '#F8FAFC',
    
    '#FFFFFF': '#FFFFFF',
    '#E2E8F0': '#E2E8F0',
    '#FFFFFF': '#FFFFFF',
    '#E2E8F0': '#E2E8F0',
    '#FFFFFF': '#FFFFFF',
    '#E2E8F0': '#E2E8F0',
    
    '#FFFFFF': '#FFFFFF',
    '#E2E8F0': '#E2E8F0',
    
    # White text from before that was replaced with rgba(28,30,33,...) 
    '#334155': '#334155',
    '#1E293B': '#1E293B',
    '#334155': '#334155',
    '#94A3B8': '#94A3B8',
    '#64748B': '#64748B',
    '#94A3B8': '#94A3B8',
    '#64748B': '#64748B',
    '#94A3B8': '#94A3B8',
    '#94A3B8': '#94A3B8',
    '#64748B': '#64748B',
    
    # Borders
    'border: 1px solid #E2E8F0': 'border: 1px solid #E2E8F0',
    'border: 1px solid #E2E8F0': 'border: 1px solid #E2E8F0',
    'border: 1px solid #E2E8F0': 'border: 1px solid #E2E8F0',
    'border: 1px solid #E2E8F0': 'border: 1px solid #E2E8F0',
}

files = glob.glob("*.py")
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original = content
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Adjust specific classes that were too colorful
        content = content.replace(".camp-card.high   { background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #DC2626; }", ".camp-card.high   { background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #DC2626; }")
        content = content.replace(".camp-card.medium { background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #D97706; }", ".camp-card.medium { background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #D97706; }")
        content = content.replace(".camp-card.low    { background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #059669; }", ".camp-card.low    { background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #059669; }")

        content = content.replace(".alert-box {\n    background: #FFFFFF;", ".alert-box {\n    background: #FFFFFF;\n    box-shadow: 0 1px 2px #F8FAFC;")
        
        if original != content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Palette upgraded in {f}")
    except Exception as e:
        print(f"Error in {f}: {e}")
print("Done.")