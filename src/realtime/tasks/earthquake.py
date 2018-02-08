# coding=utf-8

import logging
import os

from realtime.celery_app import app
from realtime.earthquake.process_event import process_event
from realtime.earthquake.settings import GRID_FILE_DEFAULT_LOCATION
from realtime.settings import EARTHQUAKE_WORKING_DIRECTORY
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/16/16'


# Initialized in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


@app.task(
    name='realtime.tasks.earthquake.process_shake', queue='inasafe-realtime')
def process_shake(event_id=None, grid_file=None, source_type='initial'):
    """Celery task for shake hazard.

    :param event_id: Event id of shake
    :type event_id: str

    :param grid_file: Grid file location relative to shakemap working
        directory
    :type grid_file: str

    :param source_type: The type of grid source. Available value:
        initial, post-processed
    :type source_type: str

    :return:
    """
    LOGGER.info('-------------------------------------------')

    if not grid_file:
        # Assume default grid file location
        working_directory = EARTHQUAKE_WORKING_DIRECTORY
        grid_file = GRID_FILE_DEFAULT_LOCATION.format(shake_id=event_id)
        grid_file_path = os.path.join(working_directory, grid_file)
    else:
        grid_file_path = grid_file

    try:
        result = process_event(
            shake_id=event_id,
            grid_file=grid_file_path,
            source_type=source_type,
            output_dir=os.path.dirname(grid_file_path))
        LOGGER.info('Process event end.')
        return vars(result)
    except BaseException as e:
        LOGGER.exception(e)
        raise
