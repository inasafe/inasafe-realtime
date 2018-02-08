# coding=utf-8
import logging

from realtime.ash.process_events import process_event
from realtime.celery_app import app
from realtime.settings import ASH_WORKING_DIRECTORY
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/16/16'


# Initialized in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


@app.task(
    name='realtime.tasks.flood.process_ash', queue='inasafe-realtime')
def process_ash(
        ash_file_path, volcano_name, region,
        latitude, longitude, alert_level,
        event_time, eruption_height, vent_height, forecast_duration):
    """Celery tasks to process ash hazard.

    :param ash_file_path: File path to ash layer
    :type ash_file_path: str

    :param volcano_name: The volcano name
    :type volcano_name: str

    :param region: The region where the volcano located
    :type region: str

    :param latitude: Latitude number in EPSG:4326
    :type latitude: float

    :param longitude: Longitude number in EPSG:4326
    :type longitude: float

    :param alert_level: Alert level string. Alailable value:
        Normal, Warning, Advisory, Watch
    :type alert_level: str

    :param event_time: Event time of Ash with timezone
    :type event_time: datetime.datetime

    :param eruption_height: Eruption height calculated from volcano height
        / vent height
    :type eruption_height: float

    :param vent_height: Height of volcano / Height of vent
    :type vent_height: float

    :param forecast_duration: Forecast duration of model in days
    :type forecast_duration: float
    """
    LOGGER.info('-------------------------------------------')

    working_directory = ASH_WORKING_DIRECTORY

    try:
        result = process_event(
            working_dir=working_directory,
            ash_file_path=ash_file_path,
            volcano_name=volcano_name,
            region=region,
            latitude=latitude,
            longitude=longitude,
            alert_level=alert_level,
            event_time=event_time,
            eruption_height=eruption_height,
            vent_height=vent_height,
            forecast_duration=forecast_duration)
        LOGGER.info('Process event end.')
        return vars(result)
    except BaseException as e:
        LOGGER.exception(e)
        raise
