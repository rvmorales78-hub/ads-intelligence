import sqlite3
import os
import sys

# Buscar la base de datos en múltiples ubicaciones posibles
possible_paths = [
    os.path.join('data', 'users.db'),
    os.path.join(os.path.dirname(__file__), 'data', 'users.db'),
    'users.db',
    os.path.join(os.getcwd(), 'data', 'users.db'),
]

db_path = None
for path in possible_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("❌ No se encontró la base de datos en ninguna ubicación")
    print("Buscando en:", possible_paths)
    sys.exit(1)

print(f"✅ Base de datos encontrada en: {db_path}")

# Conectar y modificar
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Mostrar usuarios actuales
print("\n" + "="*50)
print("📋 USUARIOS REGISTRADOS")
print("="*50)

users = cursor.execute("SELECT id, email, company_name, plan FROM users").fetchall()
for user in users:
    print(f"ID: {user['id']} | Email: {user['email']} | Empresa: {user['company_name']} | Plan: {user['plan']}")

print("="*50)

# Preguntar qué usuario modificar
email = input("\n✏️ Email del usuario a modificar: ")
new_plan = input("📦 Nuevo plan (basic/pro/enterprise): ")

new_plan = new_plan.lower()
if new_plan not in ['basic', 'pro', 'enterprise']:
    print("❌ Plan inválido. Usa: basic, pro, enterprise")
    sys.exit(1)

# Actualizar
cursor.execute("UPDATE users SET plan = ? WHERE email = ?", (new_plan, email))
conn.commit()

# Verificar
user = cursor.execute("SELECT id, email, plan FROM users WHERE email = ?", (email,)).fetchone()
if user:
    print(f"\n✅ Usuario actualizado: {user['email']} -> Plan: {user['plan']}")
else:
    print(f"\n❌ No se encontró el usuario: {email}")

conn.close()