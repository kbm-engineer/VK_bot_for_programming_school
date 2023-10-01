FROM python:3.11-slim

WORKDIR /app

COPY ./bot_project /app
COPY ./bot_project/requirements.txt /app

RUN pip3 install -r ./requirements.txt --no-cache-dir
