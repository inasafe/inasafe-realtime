#!/usr/bin/env bash

# Provide default celery config if it doesn't exists (not customized by user)
cp -n /home/src/inasafe/src/headless/celeryconfig_sample.py /home/src/inasafe/src/headless/celeryconfig.py

# Run xvfb
start-stop-daemon --start -b -x /usr/bin/Xvfb ${DISPLAY}
# Source InaSAFE environment
source run-env-linux.sh /usr


if [ $# -eq 2 ] && [ $1 = "prod" ] && [ $2 = "inasafe-headless" ]; then
    celery -A headless.celery_app worker -l info -Q inasafe-headless -n inasafe-headless.%h
elif [ $# -eq 2 ] && [ $1 = "prod" ] && [ $2 = "inasafe-headless-analysis" ]; then
    celery -A headless.celery_app worker -l info -Q inasafe-headless-analysis -n inasafe-headless-analysis.%h
fi
