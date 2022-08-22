FROM python
EXPOSE 5000/tcp
WORKDIR /usr/src

#ENV SERVICE_NAME=vpn_service

COPY requirements.txt .
COPY migrate.sh .
COPY start_gunicorn.sh .
COPY start_bot.sh .
COPY start.sh .
COPY script_expire_vpnkeys.sh .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY src .
