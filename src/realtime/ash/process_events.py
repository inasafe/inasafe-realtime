# coding=utf-8

import logging
import os
from errno import EEXIST

from realtime.ash.ash_hazard import AshHazard
from realtime.ash.notify_rest import notify_ash_hazard_to_rest
from realtime.ash.settings import ASH_ID_FORMAT
from realtime.utilities import realtime_logger_name

# Initialized in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


def process_event(
        working_dir, ash_file_path, volcano_name, region,
        latitude, longitude, alert_level,
        event_time, eruption_height, vent_height,
        output_dir=None, output_basename=None):
    """Process ash hazard.

    :param working_dir: Path for processing results
    :type working_dir: str

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

    :param output_dir: (Optional) if provided, will use the value for
        output directory
    :type output_dir: str

    :param output_basename: (Optional) if provided, will use value for layer
        basename
    :type output_basename: str

    """
    ash_id = ASH_ID_FORMAT.format(
        event_time=event_time,
        volcano_name=volcano_name)

    LOGGER.info('Process Ash ID: {0}'.format(ash_id))

    if not output_dir:
        output_dir = os.path.join(working_dir, ash_id)
        try:
            os.makedirs(output_dir)
        except OSError as e:
            if not e.errno == EEXIST:
                raise

    # Convert into InaSAFE Layer, if not yet.
    try:
        ash_hazard = AshHazard(
            ash_file_path=ash_file_path,
            volcano_name=volcano_name,
            region=region,
            latitude=latitude,
            longitude=longitude,
            alert_level=alert_level,
            event_time=event_time,
            eruption_height=eruption_height,
            vent_height=vent_height,
            output_dir=output_dir,
            output_basename=output_basename)

        if ash_hazard.hazard_exists and ash_hazard.is_valid():
            LOGGER.info('Hazard layer exists: {0}'.format(
                ash_hazard.hazard_path))
    except BaseException as e:
        LOGGER.exception(e)
        LOGGER.info('Hazard layer preparation failed.')

    LOGGER.info('Successfully processed Ash ID {0}'.format(ash_id))

    notify_ash_hazard_to_rest(ash_hazard)

    return True
