FROM python:3.8.10-slim

ENV PYTHONUNBUFFERED 1

# Dont remove or change the line containing ffmpeg installation
# because it takes a lot of time to reinstall this lib.
# please use a new line to install any other apt packages
RUN apt-get -y update && apt-get install ffmpeg -y --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /app

EXPOSE 8888

COPY requirements.txt .

RUN pip install --no-cache -r requirements.txt

# Configuration for cron
RUN apt-get -y update && apt-get install cron curl -y --no-install-recommends && rm -rf /var/lib/apt/lists/*
COPY cronjobs /etc/cron.d/cronjobs
RUN chmod 0644 /etc/cron.d/cronjobs && crontab /etc/cron.d/cronjobs

COPY . .

CMD cron && python main.py