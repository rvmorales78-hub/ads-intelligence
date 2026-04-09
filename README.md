# Ads Intelligence

Aplicación Python para extraer métricas de Facebook Marketing, analizar el rendimiento y presentar recomendaciones en un dashboard premium.

## Estructura del proyecto

- `config.py` - Configuración de entorno y logging.
- `facebook_client.py` - Conexión con Meta Marketing API, verificación de token y consultas de insights.
- `storage.py` - Guardado raw en Parquet y archivo maestro consolidado.
- `analyzer.py` - Cálculo de KPIs, reglas de decisión y generación de resumen.
- `dashboard.py` - Dashboard web con Streamlit y gráficos Plotly.
- `main.py` - Ingestión diaria de datos para ejecutar desde la línea de comandos.
- `.env.example` - Variables de entorno.
- `requirements.txt` - Dependencias exactas.

## Primeros pasos

1. Clona o copia el proyecto en tu máquina.
2. Crea un archivo `.env` basado en `.env.example`.
3. Completa los valores:
   - `APP_ID`
   - `ACCESS_TOKEN`
   - `AD_ACCOUNT_ID`
   - `AVERAGE_PRODUCT_VALUE` (opcional)
   - `FB_API_VERSION` (por defecto `v20.0`)
   - `APP_SECRET` es opcional y solo necesario si desea verificar el token con el app secret.

## Crear la app en Meta

1. Ve a [Facebook for Developers](https://developers.facebook.com/).
2. Crea una nueva aplicación.
3. Habilita el producto "Marketing API".
4. Genera un token de acceso de largo plazo (`access token`) para la cuenta publicitaria.
5. Asegúrate de que el token tenga permisos: `ads_management`, `ads_read`, `business_management`.

## Instalar dependencias

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecución

### Modo normal (dashboard)

```powershell
streamlit run dashboard.py
```

Dentro del dashboard, puedes:
- Guardar las credenciales de Facebook directamente en `.env`.
- Cargar perfiles guardados.
- Eliminar credenciales actuales.
- Eliminar perfiles de usuario guardados.

### Ejecución de ingestión diaria

```powershell
python main.py
```

## Notas importantes sobre la API de Meta

- La API de Meta NO permite obtener `reach` con desgloses diarios después de 13 meses.
- El token de acceso expira cada 60 días. Este proyecto valida el token y muestra una renovación guiada; no renueva automáticamente.
- Para periodos mayores a 30 días, el cliente intenta usar `async=true` para la consulta de `get_insights`.
- La API requiere separar métricas de entrega y de conversión, por lo que este proyecto realiza dos consultas y luego une los resultados.

## Consideraciones de producción

- `data/raw/YYYY-MM-DD/` guarda los datos crudos diarios.
- `data/processed/ads_master.parquet` guarda el histórico consolidado.
- `app.log` registra eventos de info, warning y error.
- Usa `VALIDATE_ENV` antes de ejecutar para asegurar que todas las variables estén configuradas.

## Limitaciones conocidas

- Si tu token ha expirado, debes generar uno nuevo manualmente desde Facebook for Developers.
- Para grandes rangos de fechas la API puede tardar más; la implementación usa polling para trabajos async.
- Las métricas de calidad (`quality_ranking`, `engagement_rate_ranking`, `conversion_rate_ranking`) están sujetas a disponibilidad en la cuenta.
