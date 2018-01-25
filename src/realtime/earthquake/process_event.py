# coding=utf-8

import logging

from realtime.earthquake.notify_rest import notify_realtime_rest, \
    notify_shake_hazard_to_rest
from realtime.earthquake.settings import EQ_GRID_ALGORITHM
from realtime.earthquake.shake_hazard import ShakeHazard
from realtime.settings import INASAFE_FORCE
from realtime.utilities import realtime_logger_name

# Initialised in realtime.__init__
LOGGER = logging.getLogger(realtime_logger_name())


def process_event(shake_id=None, grid_file=None, source_type=None,
                  output_dir=None):
    """Process event and convert it to hazard layer

    :param shake_id: (optional) Suspected shake_id (taken from folder name)
    :type shake_id: str

    :param grid_file: filepath of grid.xml
    :type grid_file: str

    :param source_type: The type of grid source. Available value:
        initial, post-processed
    :type source_type: str

    :param output_dir: optional output location
    :type output_dir: str

    :return: Return True if succeeded
    :rtype: bool
    """

    LOGGER.info('Processing suspected shake_id: {0}'.format(shake_id))

    # Use cached data where available
    # Whether we should always regenerate the products
    force_flag = INASAFE_FORCE
    algorithm = EQ_GRID_ALGORITHM

    # Convert Grid into InaSAFE Layer
    try:
        shake_hazard = ShakeHazard(
            grid_file=grid_file, force_flag=force_flag, algorithm=algorithm,
            source_type=source_type, output_dir=output_dir)
        if shake_hazard.hazard_exists:
            LOGGER.info('Hazard layer exists: {0}'.format(
                shake_hazard.hazard_path))
            notify_realtime_rest(shake_hazard.timestamp)
    except BaseException as e:
        LOGGER.exception(e)
        LOGGER.info('Hazard layer preparation failed.')
        return False

    LOGGER.info('Successfully processed Shake ID: {0}'.format(shake_id))

    # inform new hazard file to InaSAFE Django
    ret = notify_shake_hazard_to_rest(shake_hazard)
    LOGGER.info('Is Push successful? %s' % bool(ret))

    return True
