# coding=utf-8
"""
Celery configuration file
"""
import os
import ast

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '12/30/15'


# This is a default value
broker_url = os.environ.get('INASAFE_REALTIME_BROKER_HOST')

result_backend = broker_url

task_routes = {
    'realtime.tasks.flood': {
        'queue': 'inasafe-realtime'
    },
    'realtime.tasks.earthquake': {
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

task_always_eager = ast.literal_eval(os.environ.get(
    'task_always_eager', 'False'))

FLOOD_WORKING_DIRECTORY = os.environ.get(
    'FLOODMAPS_DIR')
EARTHQUAKE_WORKING_DIRECTORY = os.environ.get(
    'SHAKEMAPS_DIR')
ASH_WORKING_DIRECTORY = os.environ.get(
    'ASHMAPS_DIR')
