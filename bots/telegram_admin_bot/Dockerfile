FROM python:latest

WORKDIR /usr/telegram_admin_bot

COPY requirements.txt .


RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .
