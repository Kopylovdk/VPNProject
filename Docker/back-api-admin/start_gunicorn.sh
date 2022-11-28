#!/bin/sh
exec gunicorn vpnservice.wsgi -b 0.0.0.0:8000 -w 2
#./sh_scripts/start_gunicorn.sh &
#./sh_scripts/start_scheduler.sh
