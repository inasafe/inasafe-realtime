#!/usr/bin/env bash

# Wait run xvfb
while [ -z  "$(pidof /usr/bin/Xvfb)" ]; do
  start-stop-daemon --start -b -x /usr/bin/Xvfb ${DISPLAY}
  sleep 5
done

echo "Xvfb pid $(pidof /usr/bin/Xvfb)"

cp -n /home/app/realtime/celeryconfig_sample.py /home/app/realtime/celeryconfig.py

if [ $# -eq 2 ] && [ $1 = "prod" ] && [ $2 = "inasafe-realtime-worker" ]; then
    /usr/local/bin/celery -A realtime.celery_app worker -l info -Q inasafe-realtime -n inasafe-realtime.%h
elif [ $# -eq 2 ] && [ $1 = "prod" ] && [ $2 = "inasafe-realtime-monitor" ]; then
	python realtime/earthquake/notify_new_shake.py ${SHAKEMAPS_DIR}
fi

exec "$@"
