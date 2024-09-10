# Use an ARM-compatible Python base image
FROM python:3.12.4-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies and Chromium browser for ARM64
RUN apt-get update && apt-get upgrade -y && apt-get -y install  \
    gcc \
    wget \ 
    gnupg2 \
    libpq-dev \
    default-libmysqlclient-dev \
    pkg-config 

RUN apt-get -y install chromium-driver

RUN apt-get -y install chromium 
RUN apt-get purge --auto-remove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN which chromium
RUN which chromedriver

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

COPY . /app/

EXPOSE 80

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
