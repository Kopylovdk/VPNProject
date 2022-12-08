FROM python:3.11-alpine

WORKDIR /usr/telegram_client_bot

COPY requirements.txt .

#ENV TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
#ENV USERNAME=${USERNAME}
#ENV PASSWORD=${PASSWORD}

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .
