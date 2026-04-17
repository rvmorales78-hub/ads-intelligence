@echo off
echo ==========================================
echo    Iniciando Ads Intelligence...
echo ==========================================

echo.
echo [1/3] Activando entorno virtual...
call .venv\Scripts\activate.bat

echo.
echo [2/3] Instalando dependencias (si faltan)...
pip install -r requirements.txt

echo.
echo [3/3] Levantando el servidor web en segundo plano...
start "" pythonw -m streamlit run landing.py

exit