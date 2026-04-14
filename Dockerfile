FROM python:3.11-slim

WORKDIR /app

# Copiar archivo de dependencias primero (mejora la caché)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto de Streamlit
EXPOSE 8501

# Comando para iniciar la app
CMD ["streamlit", "run", "landing.py", "--server.port=8501", "--server.address=0.0.0.0"]