# coding=utf-8
import logging

import pytz

from realtime.celery_app import app
from realtime.flood.process_events import process_event
from realtime.settings import FLOOD_WORKING_DIRECTORY
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/16/16'


# Initialized in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


@app.task(
    name='realtime.tasks.flood.process_flood', queue='inasafe-realtime')
def process_flood(
        flood_id=None, time_zone=pytz.timezone('Asia/Jakarta'),
        data_source='petabencana', data_source_args=None):
    """Celery task for flood hazard.
    :param flood_id: (Optional) if provided, will use the value for
        id
    :type flood_id: str

    :param time_zone: Timezone of Flood Hazard
    :type time_zone: pytz.tzinfo.DstTzInfo

    :param data_source: Data Source type
    :type data_source: str

    :param data_source_args: (Optional).Supply this for Data Source API method
    :type data_source_args: dict
    """
    LOGGER.info('-------------------------------------------')

    working_directory = FLOOD_WORKING_DIRECTORY

    if not data_source_args:
        data_source_args = {
            'duration': 6,
            'level': 'rw'
        }
    try:
        process_event(
            working_dir=working_directory,
            flood_id=flood_id,
            time_zone=time_zone,
            data_source=data_source,
            data_source_args=data_source_args)
        LOGGER.info('Process event end.')
        return True
    except Exception as e:
        LOGGER.exception(e)

    return False
