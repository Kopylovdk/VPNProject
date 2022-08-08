#!/bin/sh

exec gunicorn vpnservice.wsgi -b 0.0.0.0:5000 -w 2
