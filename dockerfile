# Use an ARM-compatible Python base image
FROM python:3.12.4-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies and Chromium browser for ARM64
RUN apt-get update && apt-get -y install \
    gcc \
    libpq-dev \
    default-libmysqlclient-dev \
    pkg-config \
    wget \
    curl \
    unzip \
    chromium \
    libnss3 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    libatk-bridge2.0-0 \
    libgbm1 \
    xdg-utils && \
    apt-get clean

# Install specific Chromedriver for arm64 architecture
RUN wget -q https://github.com/electron/electron/releases/download/v21.2.0/chromedriver-v21.2.0-linux-arm64.zip -O /tmp/chromedriver-linux-arm64.zip && \
    unzip /tmp/chromedriver-linux-arm64.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver-linux-arm64.zip

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

COPY . /app/

EXPOSE 80

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
