FROM python:latest

WORKDIR /usr/telegram_client_bot

COPY requirements.txt .


RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .
