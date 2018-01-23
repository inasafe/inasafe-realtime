# coding=utf-8
import logging

import requests

from realtime.exceptions import RESTRequestFailedError
from realtime.push_rest import (
    InaSAFEDjangoREST)
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '12/01/15'

LOGGER = logging.getLogger(realtime_logger_name())


def notify_flood_hazard_to_rest(flood_hazard, fail_silent=True):
    """Pushing flood hazard description to REST server.

    :param flood_hazard: The flood event to push
    :type flood_hazard: realtime.flood.flood_hazard.FloodHazard

    :param fail_silent: If set True, will still continue whan the push process
        failed. Default vaule to True. If False, this method will raise
        exception.
    :type fail_silent:

    :return: Return True if successfully pushed data
    :rtype: bool
    """
    if flood_hazard.impacted_hazard_features == 0:
        LOGGER.info('No potential impact exists. Will not push anything')
        return

    inasafe_django = InaSAFEDjangoREST()
    # check credentials exists in os.environ
    if not inasafe_django.is_configured():
        LOGGER.info('Insufficient information to push flood event to '
                    'Django Realtime')
        LOGGER.info('Please set environment for INASAFE_REALTIME_REST_URL, '
                    'INASAFE_REALTIME_REST_LOGIN_URL, '
                    'INASAFE_REALTIME_REST_USER, and '
                    'INASAFE_REALTIME_REST_PASSWORD')
        return

    # set headers and cookie
    # begin communicating with server
    LOGGER.info('----------------------------------')
    LOGGER.info('Push data to REST server: %s', inasafe_django.base_url())
    try:
        session = inasafe_django.rest

        # build the data request:
        flood_data = {
            'event_id': flood_hazard.flood_id,
            'hazard_path': flood_hazard.hazard_path,
            'data_source': flood_hazard.data_source.source_name(),
            'time': flood_hazard.event_time,
            'interval': flood_hazard.duration,
            'source': flood_hazard.data_source.source_key(),
            'region': flood_hazard.data_source.region_name()
        }

        # modify headers
        headers = {
            'X-CSRFTOKEN': inasafe_django.csrf_token,
        }

        # check does the flood event already exists?
        response = session.flood(
            flood_data['event_id']).GET()
        if response.status_code == requests.codes.ok:
            # event exists, we should update using PUT Url
            response = session.flood(
                flood_data['event_id']).PUT(
                data=flood_data,
                headers=headers)
        elif response.status_code == requests.codes.not_found:
            # event does not exists, create using POST url
            response = session.flood.POST(
                data=flood_data,
                headers=headers)

        if not (response.status_code == requests.codes.ok or
                response.status_code == requests.codes.created):
            # raise exceptions
            error = RESTRequestFailedError(
                url=response.url,
                status_code=response.status_code,
                data=flood_data)
            if fail_silent:
                LOGGER.warning(error.message)
            else:
                raise error
        return True
    # pylint: disable=broad-except
    except Exception as exc:
        if fail_silent:
            LOGGER.warning(exc)
        else:
            raise exc
