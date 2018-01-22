# coding=utf-8
"""
Settings file for Shakemap Realtime
"""
import os

from safe.gui.tools.shake_grid.shake_grid import USE_ASCII

# Grid xml file pattern to catch
GRID_FILE_PATTERN = os.environ.get(
    'GRID_FILE_PATTERN',
    '(?P<shake_id>\d{14})/grid\.xml$')

GRID_FILE_DEFAULT_LOCATION = os.environ.get(
    'GRID_FILE_DEFAULT_LOCATION',
    '{shake_id}/grid.xml')

# INASAFE Locale used
INASAFE_LOCALE = os.environ.get(
    'INASAFE_LOCALE',
    'en')

SHAKE_TIMESTAMP_FORMAT = os.environ.get(
    'SHAKE_TIMESTAMP_FORMAT',
    '')

EQ_GRID_SOURCE = os.environ.get('EQ_GRID_SOURCE')

EQ_GRID_SOURCE_TYPE = os.environ.get('EQ_GRID_SOURCE_TYPE', 'initial')

EQ_GRID_ALGORITHM = os.environ.get('EQ_GRID_ALGORITHM', USE_ASCII)
