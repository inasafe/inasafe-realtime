# coding=utf-8
"""
Celery configuration file
"""
import ast
import logging
import os

from realtime.utilities import realtime_logger_name

LOGGER = logging.getLogger(realtime_logger_name())


# This is a default value
broker_url = os.environ.get('INASAFE_REALTIME_BROKER_HOST')
LOGGER.info('Broker url {0}'.format(broker_url))

result_backend = broker_url

task_routes = {
    'realtime.tasks.flood': {
        'queue': 'inasafe-realtime'
    },
    'realtime.tasks.earthquake': {
        'queue': 'inasafe-realtime'
    },
    'realtime.tasks.ash': {
        'queue': 'inasafe-realtime'
    }
}

# RMN: This is really important.

# Long bug description ahead! Beware.

# This set InaSAFE Headless concurrency to 1. Which means this celery worker
# will only uses 1 thread. This is necessary because we are using Xvfb to
# handle graphical report generation (used by processing framework).
# Somehow, qgis processing framework is not thread safe. It forgot to call
# XInitThreads() which is necessary for multithreading. Read long description
# here about XInitThreads(): http://www.remlab.net/op/xlib.shtml
# In other words, you should always set this to 1. If not, it will default to
# number of CPUs/core which can be multithreaded and will invoke debugging
# **NIGHTMARE** to your celery worker. Read about this particular settings
# here:
# http://docs.celeryproject.org/en/3.1/configuration.html#celeryd-concurrency
worker_concurrency = 1
worker_prefetch_multiplier = 1

# Celery config
task_serializer = 'pickle'
accept_content = {'pickle'}
result_serializer = 'pickle'


# Late ACK settings
task_acks_late = True
task_reject_on_worker_lost = True

task_always_eager = ast.literal_eval(os.environ.get(
    'TASK_ALWAYS_EAGER', 'False'))
