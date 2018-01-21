# coding=utf-8

import logging
import os
import re
from datetime import datetime

import pytz
from realtime.exceptions import EventIdError
from realtime.utilities import realtime_logger_name

from realtime.flood.data_source import load_data_api_object
from realtime.flood.flood_hazard import FloodHazard
from realtime.flood.settings import FLOOD_ID_FORMAT, FLOOD_ID_REGEXP, \
    FLOOD_HAZARD_DEFAULT_BASENAME

# Initialized in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


def process_event(
        working_dir, flood_id=None, time_zone=None,
        output_dir=None, data_source=None,
        data_source_args=None):
    """Process floodmap event.

    :param working_dir: Path for processing results
    :type working_dir: str

    :param flood_id: (Optional) if provided, will use the value for
        id
    :type flood_id: str

    :param output_dir: (Optional) if provided, will use the value for
        output directory
    :type output_dir: str

    :param data_source: Data Source type
    :type data_source: str

    :param data_source_args: Supply this for Data Source API method
    :type data_source_args: dict

    :param
    """

    event_time = None
    duration = None
    level = None

    if not flood_id:
        event_time = datetime.utcnow().replace(tzinfo=pytz.utc)
        duration = 6
        level = 'rw'
        flood_id = FLOOD_ID_FORMAT.format(
            time=event_time, duration=duration, level=level)
    else:
        # validate flood id
        if not validate_flood_id(flood_id):
            raise EventIdError('Specified Flood event ID have wrong format.')

        # parse event time
        event_time, duration, level = parse_flood_id(flood_id)

    if not time_zone:
        # Use default timezone: Jakarta
        time_zone = pytz.timezone('Asia/Jakarta')

    LOGGER.info('Process Flood ID: {id}'.format(id=flood_id))

    # If not specified, default to PetaBencana
    if not data_source:
        data_source = 'petabencana'

    # load datasource class
    data_api = load_data_api_object(data_source)

    if not data_source_args:
        data_source_args = {}
    geo_json_result = data_api.get_aggregate_report(**data_source_args)

    # If not specified, default to flood id
    if not output_dir:
        output_dir = flood_id

    # Use default basename
    output_basename = FLOOD_HAZARD_DEFAULT_BASENAME

    geojson_file_path = os.path.join(
        working_dir, output_dir, '{basename}.json'.format(
            basename=output_basename))

    try:
        os.makedirs(os.path.dirname(geojson_file_path))
    except OSError:
        pass

    # Write GeoJSON result to file
    with open(geojson_file_path, 'w') as f:
        f.write(geo_json_result)

    # Convert into InaSAFE Layer
    try:
        flood_hazard = FloodHazard(
            flood_id, event_time, time_zone, duration, level,
            geojson_file_path,
            data_api)

        if flood_hazard.hazard_exists:
            LOGGER.info('Hazard layer exists: {0}'.format(
                flood_hazard.hazard_path))
    except BaseException as e:
        LOGGER.exception(e)
        LOGGER.info('Hazard layer preparation failed.')

    LOGGER.info('Successfully processed Flood ID {0}'.format(flood_id))

    return True


def validate_flood_id(flood_id):
    """Validate flood id format.

    :param flood_id: Agreed Flood ID
    :type flood_id: str
    """

    try:
        event_time, duration, level = parse_flood_id(flood_id)

        allowed_duration = [1, 3, 6]

        if duration not in allowed_duration:
            return False

        allowed_level = ['subdistrict', 'village', 'rw']

        if level not in allowed_level:
            return False

    except BaseException:
        return False

    return True


def parse_flood_id(flood_id):
    """Parse flood id Information.

    :return: Tuple of event_time, duration, level
    :rtype: (datetime.datetime,int,str)
    """
    prog = re.compile(FLOOD_ID_REGEXP)
    result = prog.match(flood_id)

    year = int(result.group('year'))
    month = int(result.group('month'))
    day = int(result.group('day'))
    hour = int(result.group('hour'))
    duration = int(result.group('_duration'))
    level = result.group('_level')

    event_time = datetime(year, month, day, hour, tzinfo=pytz.utc)
    return event_time, duration, level
