import os
import re

files_to_fix = ['landing.py', 'auth.py', 'client_dashboard.py', 'admin_dashboard.py', 'app.py', 'pages/app.py', 'pages/reset_admin_endpoint.py']

replacements = {
    '#F5F3FF': '#1c1e21',
    'rgba(232,230,240,': 'rgba(28,30,33,',
    'rgba(255,255,255,0.06)': 'rgba(0,0,0,0.04)',
    'rgba(255,255,255,0.1)': 'rgba(0,0,0,0.1)',
    'rgba(255,255,255,0.02)': 'rgba(0,0,0,0.02)',
    'rgba(255,255,255,0.05)': 'rgba(0,0,0,0.05)',
    'rgba(255,255,255,0.03)': 'rgba(0,0,0,0.03)',
    'rgba(255,255,255,0.04)': 'rgba(0,0,0,0.04)',
    'rgba(255,255,255,0.08)': 'rgba(0,0,0,0.08)',
    'rgba(255,255,255,0.12)': 'rgba(0,0,0,0.12)'
}

for filepath in files_to_fix:
    if not os.path.exists(filepath): continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Colors replaced.")
