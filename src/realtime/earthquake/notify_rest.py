# coding=utf-8
import json
import logging

import pytz
import requests

from realtime.exceptions import RESTRequestFailedError
from realtime.push_rest import InaSAFEDjangoREST
from realtime.settings import INASAFE_REALTIME_DATETIME_FORMAT
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/07/15'

LOGGER = logging.getLogger(realtime_logger_name())


def notify_realtime_rest(timestamp):
    """Notify realtime rest that someone is logged in to realtime.

    This can indicate someone is pushing raw shakemap files

    :param timestamp: python datetime object indicating shakemap timestamp
    :type timestamp: datetime.datetime
    """
    try:
        inasafe_django = InaSAFEDjangoREST()
        LOGGER.info(timestamp)
        session = inasafe_django.rest
        timestamp_utc = timestamp.astimezone(tz=pytz.utc)
        data = {
            'timestamp': timestamp_utc.strftime(
                INASAFE_REALTIME_DATETIME_FORMAT)
        }
        headers = {
            'X-CSRFTOKEN': inasafe_django.csrf_token
        }
        LOGGER.info(
            'Is Logged in %s' % session.is_logged_in.GET(headers=headers))

        response = session.indicator.notify_shakemap_push.POST(
            data=data, headers=headers)
        # We will not handle post error, since we don't need it.
        # It just simply fails
        if response.status_code != requests.codes.ok:
            LOGGER.info(
                'Notify Shakemap Push Failed : Error code %s',
                response.status_code)
    except Exception as exc:
        LOGGER.exception(exc)


def notify_shake_hazard_to_rest(shake_hazard, fail_silent=True):
    """Pushing shake event Grid.xml description files to REST server.

    :param shake_hazard: The shake event to push
    :type shake_hazard: realtime.earthquake.shake_hazard.ShakeHazard

    :param fail_silent: If set True, will still continue whan the push process
        failed. Default vaule to True. If False, this method will raise
        exception.
    :type fail_silent: bool

    :return: Return True if successfully pushed data
    :rtype: bool
    """
    inasafe_django = InaSAFEDjangoREST()
    # check credentials exists in os.environ
    if not inasafe_django.is_configured():
        LOGGER.info('Insufficient information to push shake map to '
                    'Django Realtime')
        LOGGER.info('Please set environment for INASAFE_REALTIME_REST_URL, '
                    'INASAFE_REALTIME_REST_LOGIN_URL, '
                    'INASAFE_REALTIME_REST_USER, and '
                    'INASAFE_REALTIME_REST_PASSWORD')
        return False

    # set headers and cookie
    # begin communicating with server
    LOGGER.info('----------------------------------')
    LOGGER.info('Push data to REST server: %s', inasafe_django.base_url())
    try:
        session = inasafe_django.rest
        headers = {
            'X-CSRFTOKEN': inasafe_django.csrf_token,
            'Content-Type': 'application/json'
        }

        # build the data request:
        earthquake_data = {
            'shake_id': shake_hazard.event_id,
            'source_type': shake_hazard.source_type,
            'hazard_path': shake_hazard.hazard_path,
            'magnitude': shake_hazard.magnitude,
            'depth': shake_hazard.depth,
            'time': str(shake_hazard.timestamp),
            'location': {
                'type': 'Point',
                'coordinates': [
                    shake_hazard.longitude,
                    shake_hazard.latitude
                ]
            },
            'location_description': shake_hazard.location
        }

        earthquake_file = {
            'shake_grid': (
                '{shake_id}-grid.xml'.format(shake_id=shake_hazard.event_id),
                open(shake_hazard.grid_file))
        }

        # check does the shake event already exists?
        response = session.earthquake(
            earthquake_data['shake_id'],
            earthquake_data['source_type']).GET()
        if response.status_code == requests.codes.ok:
            # event exists, we should update using PUT Url
            response = session.earthquake(
                earthquake_data['shake_id'],
                earthquake_data['source_type']).PUT(
                data=json.dumps(earthquake_data),
                headers=headers)
        elif response.status_code == requests.codes.not_found:
            # event does not exists, create using POST url
            response = session.earthquake.POST(
                data=json.dumps(earthquake_data),
                headers=headers)

        # upload grid.xml
        headers = {
            'X-CSRFTOKEN': inasafe_django.csrf_token,
        }
        if response.status_code == requests.codes.ok:
            response = session.earthquake(
                earthquake_data['shake_id'],
                earthquake_data['source_type']).PUT(
                files=earthquake_file,
                headers=headers)

        if not (response.status_code == requests.codes.ok
                or response.status_code == requests.codes.created):
            # raise exceptions
            error = RESTRequestFailedError(
                url=response.url,
                status_code=response.status_code,
                data=json.dumps(earthquake_data),
                files=earthquake_file)
            if fail_silent:
                LOGGER.info(error.message)
            else:
                raise error

        return True
    # pylint: disable=broad-except
    except Exception as exc:
        if fail_silent:
            LOGGER.warning(exc)
        else:
            raise exc
