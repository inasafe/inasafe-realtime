#!/usr/bin/env bash

# Run xvfb
start-stop-daemon --start -b -x /usr/bin/Xvfb ${DISPLAY}
# Source InaSAFE environment
source /run-env-linux.sh /usr


if [ $# -eq 2 ] && [ $1 = "prod" ] && [ $2 = "inasafe-realtime-worker" ]; then
	cp -n /home/app/realtime/celeryconfig_sample.py /home/app/realtime/celeryconfig.py
    /usr/local/bin/celery -A realtime.celery_app worker -l info -Q inasafe-headless -n inasafe-headless.%h
elif [ $# -eq 2 ] && [ $1 = "prod" ] && [ $2 = "inasafe-realtime-monitor" ]; then
	python realtime/earthquake/notify_new_shake.py /home/realtime/shakemaps
elif [ $# -eq 1 ] && [ $1 = "dev" ]; then
	/usr/sbin/sshd -D
fi
