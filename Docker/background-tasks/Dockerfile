FROM python:3.11-alpine

WORKDIR /usr/src

COPY requirements.txt .

COPY src/apps/outline_vpn_admin/management apps/outline_vpn_admin/management
COPY src/apps/outline_vpn_admin/apps.py apps/outline_vpn_admin
COPY src/apps/outline_vpn_admin/exceptions.py apps/outline_vpn_admin
COPY src/apps/outline_vpn_admin/models.py apps/outline_vpn_admin
COPY src/apps/outline_vpn_admin/outline_api.py apps/outline_vpn_admin
COPY src/apps/outline_vpn_admin/scripts.py apps/outline_vpn_admin

COPY src/vpnservice vpnservice
COPY Docker/background-tasks/start_scheduler.sh sh_scripts/
COPY Docker/background-tasks/urls.py vpnservice
COPY Docker/background-tasks/settings.py vpnservice
COPY src/config.yaml .
COPY src/manage.py .
COPY src/logs/config logs/config

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

