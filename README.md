# Ads Intelligence SaaS

Ads Intelligence es una plataforma SaaS (Software as a Service) premium diseñada para revolucionar la forma en que las agencias y anunciantes gestionan sus campañas de Facebook Ads. Convierte los datos crudos de Meta en insights procesables, priorizados y fáciles de entender, automatizando el análisis y la toma de decisiones.

## 🚀 Ventajas y Beneficios

- **Inteligencia Accionable:** Olvídate de mirar tablas interminables. El sistema te dice exactamente qué campañas detener (**Kill**), cuáles corregir (**Fix**) y cuáles escalar (**Scale**).
- **Ahorro de Tiempo:** Reduce las horas de auditoría manual a segundos gracias al Account Health Score y al resumen diario.
- **Multicuenta Real:** Ideal para agencias o freelancers. Gestiona múltiples cuentas publicitarias (Business Managers) de diferentes clientes desde una sola interfaz.
- **Modelo de Negocio SaaS Integrado:** Incluye sistema de registro, autenticación, control de roles (Admin/Cliente) y un modelo **Freemium** con un plan gratuito de base.
- **Despliegue Rápido:** Arquitectura lista para producción con soporte para SQLite (desarrollo) y PostgreSQL (producción), con configuraciones para Docker y Fly.io.

## ⚙️ Funcionalidades Principales

1. **Dashboard de Clientes Premium (`client_dashboard.py`):**
   - **Action Center:** Acciones ordenadas por impacto y urgencia (Crítico, Oportunidad, Atención).
   - **Account Health Score:** Puntuación global de 0 a 100 evaluando rendimiento, eficiencia, audiencia y distribución de presupuesto.
   - **Mapa de Saturación:** Identifica campañas con alta frecuencia que queman a la audiencia.
   - **Gestor de Cuentas de Meta:** Añade, cambia y elimina cuentas publicitarias (App ID, Token, Account ID) cifradas en la base de datos de manera segura.
   - **Modelo Freemium:** Plan gratuito con límites para probar la plataforma, con opción de mejora a planes superiores.

2. **Panel de Administración (`admin_dashboard.py`):**
   - Gestión integral de todos los usuarios registrados.
   - Modificación de planes (Basic, Pro, Enterprise).
   - Estadísticas globales del negocio (MRR estimado, conversiones, usuarios activos).

3. **Análisis Avanzado (`analyzer.py` & `facebook_client.py`):**
   - Comparativas automáticas de CTR y CPC contra benchmarks de la industria.
   - Estimación de ROI y ROAS potencial de las campañas "Estrella".
   - Integración nativa con la API v20.0+ de Facebook Marketing.

4. **Sistema de Autenticación (`auth.py`):**
   - Registro de nuevas cuentas.
   - Login seguro con contraseñas encriptadas (SHA-256).
   - Roles jerárquicos (User, Admin).

## 📁 Estructura de la Aplicación

- `landing.py` - Punto de entrada principal y enrutador (Landing Page, Login, Registro, Dashboards).
- `auth.py` - Controladores de las pantallas de Login y Registro. Maneja el inicio de la sesión.
- `client_dashboard.py` - Interfaz principal del usuario/cliente.
- `admin_dashboard.py` - Interfaz principal del administrador.
- `analyzer.py` - Motor lógico. Procesa los dataframes de Pandas y genera el *Account Score*, las recomendaciones y alertas.
- `database.py` - Capa de persistencia. Soporta PostgreSQL (producción) o SQLite (local) automáticamente según el entorno.
- `facebook_client.py` - Cliente de conexión directa con la API de Facebook Graph.
- `run_app.py` / `start.bat` / `start.ps1` - Scripts para iniciar la aplicación localmente.
- `fly.toml` / `Dockerfile` - Archivos de configuración para despliegue en la nube.

## 🛠️ Instrucciones de Uso

### 1. Requisitos Previos
- Python 3.10 o superior.
- Una cuenta en [Meta for Developers](https://developers.facebook.com/) con una app creada y un Token de Acceso con los permisos `ads_management` y `ads_read`.

### 2. Instalación Local

```powershell
# 1. Clona o descarga el repositorio
# 2. Crea y activa tu entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Configura las variables de entorno
cp .env.example .env
# Opcional: Configura DATABASE_URL en .env si deseas usar PostgreSQL.
# Si no lo configuras, usará SQLite por defecto.

# 5. Ejecuta la aplicación
# Puedes usar el script de inicio:
.\start.ps1
# O directamente con Streamlit:
streamlit run landing.py
```

### 3. Flujo de Trabajo (Demo)
1. Abre tu navegador en `http://localhost:8501`.
2. Verás la Landing Page. Haz clic en **Comenzar Gratis**.
3. Crea una cuenta nueva. Al registrarte, se te otorgará el plan **Gratuito (Basic)**.
4. Inicia sesión con tu nueva cuenta.
5. Dentro del dashboard, expande la sección **🔑 Cuentas de Facebook Ads** y agrega tu App ID, Access Token y Account ID (ej. `act_123456789`).
6. El sistema comenzará inmediatamente a importar y procesar los datos de tus campañas.
7. *Para acceder como admin:* Si es tu primera vez, puedes ejecutar `python reset_admin.py` para crear el usuario administrador por defecto (`admin@adsintelligence.com` / `admin123`) y acceder al panel de control de usuarios.

## 🛡️ Validación de Funcionalidad

La estructura ha sido auditada exhaustivamente:
- **Sintaxis:** Todos los scripts de núcleo (`landing.py`, `auth.py`, `client_dashboard.py`, `database.py`, `analyzer.py`) están libres de errores.
- **Persistencia:** La base de datos (SQLite/PostgreSQL) gestiona correctamente los usuarios, sus planes y sus credenciales cifradas.
- **Seguridad:** Los tokens de Facebook y los IDs de cuenta se encriptan simétricamente mediante la librería `cryptography.fernet` antes de guardarse en la BD.
- **Navegación:** El ruteo dinámico de Streamlit (`st.session_state.page`) gestiona de forma fluida el paso entre Landing -> Registro -> Login -> Dashboard.