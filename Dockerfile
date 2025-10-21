FROM python:3.11-slim

WORKDIR /app

COPY . .

# Instala las dependencias necesarias del sistema para Chromium (sin las fuentes antiguas)
RUN apt-get update && apt-get install -y \
    libnss3 libxss1 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxkbcommon0 libx11-xcb1 libxcomposite1 libxdamage1 \
    libxext6 libxi6 libxrandr2 libxrender1 libxtst6 \
    libpangocairo-1.0-0 libpango-1.0-0 libglib2.0-0 libgtk-3-0 libgbm1 \
    libasound2 xdg-utils wget ca-certificates fonts-liberation fonts-unifont && \
    pip install --no-cache-dir -r requirements.txt

# 👇 Instalamos SOLO el navegador Chromium, sin dependencias del sistema (ya están arriba)
RUN playwright install chromium

EXPOSE 10000

CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
