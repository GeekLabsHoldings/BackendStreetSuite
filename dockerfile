# setup server #

# 1_start docker kernal + python 
FROM python:3.12.4-slim-bullseye

# 2_ENV to show logs 
ENV PYTHONUNBUFFERED=1  

# 3_ update kernal + install 
RUN apt-get update && apt-get -y install gcc libpq-dev

## create project folder on the kernal 
WORKDIR /app

## copy requirements file 
COPY requirements.txt /app/requirements.txt

## install requirements packages ##\
RUN pip install -r /app/requirements.txt

## copy project code to docker app dir 
COPY . /app/

################### FINISH #######################

