#!/bin/sh
exec gunicorn vpnservice.wsgi -b 0.0.0.0:443 -w 2
#exec gunicorn vpnservice.wsgi -b 0.0.0.0:8000 -w 2
