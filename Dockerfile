FROM python:3.11-slim

WORKDIR /app

# Instala dependencias necesarias para Chrome headless
RUN apt-get update && apt-get install -y \
    wget unzip xvfb libxi6 libgconf-2-4 \
    libnss3 libasound2 fonts-liberation libappindicator3-1 \
    libxss1 lsb-release xdg-utils libatk-bridge2.0-0 \
    libgtk-3-0 libdrm-dev libgbm-dev chromium chromium-driver && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Puerto dinámico para Railway
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT} app:app"]
