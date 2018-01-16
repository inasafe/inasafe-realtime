# coding=utf-8
"""Common settings for InaSAFE Realtime."""

import os
import ast

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
