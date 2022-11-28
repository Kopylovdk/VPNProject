FROM python:3.11-alpine
WORKDIR /usr/src


COPY requirements.txt .

COPY Docker/back-api-admin/makemigrations.sh sh_scripts/
COPY Docker/back-api-admin/migrate.sh sh_scripts/
COPY Docker/back-api-admin/start_gunicorn.sh sh_scripts/
COPY src/ .


RUN pip install --upgrade pip \
    && pip install -r requirements.txt


