#kernel and python
FROM python:3.11.9-slim-bullseye
#sowing logs after running server
ENV PYTHONUNBUFFERED=1
#KERNEL UPDATES AND INSTALL DEPENDENCIES
RUN  

WORKDIR /BackendStreetSuite/
COPY requirements.txt 
COPY . .
CMD [ "node", "main.js"]