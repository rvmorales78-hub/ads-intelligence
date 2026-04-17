@echo off
echo ==========================================
echo   Deteniendo Ads Intelligence...
echo ==========================================
taskkill /F /IM pythonw.exe /T >nul 2>&1
echo Servidor detenido exitosamente.
pause