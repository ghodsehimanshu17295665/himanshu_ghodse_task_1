FROM python:3.9

WORKDIR /app

COPY . /app/

#  Install netcat + dependencies
RUN apt-get update && apt-get install -y netcat

RUN pip install -r requirements.txt

RUN chmod +x /app/server-entrypoint.sh

EXPOSE 8000
