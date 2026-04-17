Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Iniciando Ads Intelligence..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host "`n[1/3] Activando entorno virtual..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

Write-Host "`n[2/3] Verificando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "`n[3/3] Levantando el servidor web..." -ForegroundColor Green
streamlit run landing.py