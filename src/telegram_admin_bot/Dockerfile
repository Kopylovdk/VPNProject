FROM python:latest
EXPOSE 5000/tcp
WORKDIR /usr/src

COPY requirements.txt .

COPY sh_scripts/* sh_scripts/


RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY src .
