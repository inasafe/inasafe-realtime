# coding=utf-8
"""Common settings for InaSAFE Realtime."""

import ast
import os

INASAFE_REALTIME_REST_USER = os.environ.get(
    'INASAFE_REALTIME_REST_USER')

INASAFE_REALTIME_REST_PASSWORD = os.environ.get(
    'INASAFE_REALTIME_REST_PASSWORD')

INASAFE_REALTIME_REST_URL = os.environ.get(
    'INASAFE_REALTIME_REST_URL')

INASAFE_REALTIME_DATETIME_FORMAT = os.environ.get(
    'INASAFE_REALTIME_DATETIME_FORMAT',
    '%Y-%m-%d %H:%M:%S')

INASAFE_FORCE = ast.literal_eval(os.environ.get(
    'INASAFE_FORCE',
    'False'))

ON_TRAVIS = ast.literal_eval(os.environ.get(
    'ON_TRAVIS',
    'False'))

FLOOD_WORKING_DIRECTORY = os.environ.get(
    'FLOODMAPS_DIR')
EARTHQUAKE_WORKING_DIRECTORY = os.environ.get(
    'SHAKEMAPS_DIR')
ASH_WORKING_DIRECTORY = os.environ.get(
    'ASHMAPS_DIR')
