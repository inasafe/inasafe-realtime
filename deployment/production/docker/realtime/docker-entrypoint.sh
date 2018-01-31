#!/usr/bin/env bash

# Run xvfb
start-stop-daemon --start -b -x /usr/bin/Xvfb ${DISPLAY}

cp -n /home/app/realtime/celeryconfig_sample.py /home/app/realtime/celeryconfig.py

if [ $# -eq 2 ] && [ $1 = "prod" ] && [ $2 = "inasafe-realtime-worker" ]; then
    /usr/local/bin/celery -A realtime.celery_app worker -l info -Q inasafe-realtime -n inasafe-realtime.%h
elif [ $# -eq 2 ] && [ $1 = "prod" ] && [ $2 = "inasafe-realtime-monitor" ]; then
	python realtime/earthquake/notify_new_shake.py /home/realtime/shakemaps
fi
