FROM python:3.12-slim

ENV APP_HOME /app
WORKDIR $APP_HOME

WORKDIR /app
COPY . ./

RUN pip install --no-cache-dir -r requirements.txt
