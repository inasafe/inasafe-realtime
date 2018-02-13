# coding=utf-8
import logging

import requests

from realtime.ash.settings import ASH_DATETIME_FORMAT, ASH_TIMESTAMP_FORMAT
from realtime.exceptions import RESTRequestFailedError
from realtime.push_rest import (
    InaSAFEDjangoREST)
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '12/01/15'

LOGGER = logging.getLogger(realtime_logger_name())


def notify_ash_hazard_to_rest(ash_hazard, fail_silent=True):
    """Push ash event to inasafe-django

    :param ash_hazard: The Ash Event
    :type ash_hazard: realtime.ash.ash_hazard.AshHazard

    :param fail_silent:
    :return:
    """
    inasafe_django = InaSAFEDjangoREST()
    # check credentials exists in os.environ
    if not inasafe_django.is_configured():
        LOGGER.info('Insufficient information to push ash event to '
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
        dateformat = ASH_DATETIME_FORMAT
        timestring = ASH_TIMESTAMP_FORMAT
        ash_data = {
            'volcano_name': ash_hazard.volcano_name,
            'event_time': dateformat.format(event_time=ash_hazard.event_time),
            'hazard_path': ash_hazard.hazard_path
        }

        # modify headers
        headers = {
            'X-CSRFTOKEN': inasafe_django.csrf_token,
        }

        # post impact results
        # Update using PUT url
        response = session.ash(
            ash_data['volcano_name'],
            timestring.format(event_time=ash_hazard.event_time)).PUT(
            data=ash_data,
            headers=headers)

        if not (response.status_code == requests.codes.ok or
                response.status_code == requests.codes.created):
            error = RESTRequestFailedError(
                url=response.url,
                status_code=response.status_code,
                data=ash_data)

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
