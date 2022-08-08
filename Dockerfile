FROM python
EXPOSE 5000/tcp
WORKDIR /usr/src

ENV SERVICE_NAME=vpn_service
ENV PATH_TO_CONF=.
ENV OUT_PATH_CONF=.


COPY requirements.txt .
COPY migrate.sh .
COPY start.sh .


RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY src .

CMD ["./start.sh"]
