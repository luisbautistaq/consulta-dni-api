# Usa una versión estable y soportada de Python
FROM python:3.11-slim

# Define la carpeta dentro del contenedor donde se ejecutará todo
WORKDIR /app

# Copia todos tus archivos del proyecto a esa carpeta
COPY . .

# Instala todas las librerías del sistema que necesita Playwright (Chromium headless)
RUN apt-get update && apt-get install -y \
    libnss3 libxss1 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxkbcommon0 libx11-xcb1 libxcomposite1 libxdamage1 \
    libxext6 libxi6 libxrandr2 libxrender1 libxtst6 \
    libpangocairo-1.0-0 libpango-1.0-0 libglib2.0-0 libgtk-3-0 libgbm1 \
    libasound2 xdg-utils wget ca-certificates fonts-liberation && \
    pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps chromium

# Expone el puerto donde correrá Flask/Gunicorn (Render usa el 10000 por defecto)
EXPOSE 10000

# Indica el comando que inicia tu app (como "python app.py")
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
