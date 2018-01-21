# coding=utf-8
import json
import logging

import requests
from realtime.utilities import realtime_logger_name

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '11/23/15'


LOGGER = logging.getLogger(realtime_logger_name())


class FloodHazardBaseClassAPI(object):

    @classmethod
    def get_aggregate_report(cls, *args, **kwargs):
        raise Exception(
            'This method should be overridden by inherited class.')

    @classmethod
    def source_name(cls):
        raise Exception(
            'This method should be overridden by inherited class.')

    @classmethod
    def source_key(cls):
        raise Exception(
            'This method should be overridden by inherited class.')

    @classmethod
    def region_name(cls):
        raise Exception(
            'This method should be overridden by inherited class.')


class PetaJakartaAPI(FloodHazardBaseClassAPI):

    @classmethod
    def get_aggregate_report(cls, duration, level):
        rest_point = (
            'https://rem.petajakarta.org/banjir/data/api/v2/rem/flooded')
        params = {
            'format': 'geojson'
        }
        r = requests.get(rest_point, params=params, verify=False)
        if not r.status_code == requests.codes.ok:
            LOGGER.error("Can't access API")
            return
        return r.text

    @classmethod
    def source_name(cls):
        return 'PetaJakarta'

    @classmethod
    def source_key(cls):
        return 'petajakarta'

    @classmethod
    def region_name(cls):
        return 'Jakarta'


class PetaBencanaDevAPI(FloodHazardBaseClassAPI):

    @classmethod
    def get_aggregate_report(cls, duration, level):

        rest_point = (
            'https://data-dev.petabencana.id/floods')
        params = {
            'city': 'jbd',
            'geoformat': 'geojson',
            'format': 'json',
            'minimum_state': 1
        }
        r = requests.get(rest_point, params=params, verify=False)
        if not r.status_code == requests.codes.ok:
            LOGGER.error("Can't access API")
            return
        features = r.json()['result']

        return json.dumps(features)

    @classmethod
    def source_name(cls):
        return 'PetaBencana - Development API'

    @classmethod
    def source_key(cls):
        return 'petabencana-dev'

    @classmethod
    def region_name(cls):
        return 'Jakarta'


class PetaBencanaAPI(FloodHazardBaseClassAPI):

    @classmethod
    def get_aggregate_report(cls, duration, level):

        rest_point = (
            'https://data.petabencana.id/floods')
        params = {
            'city': 'jbd',
            'geoformat': 'geojson',
            'format': 'json',
            'minimum_state': 1
        }
        r = requests.get(rest_point, params=params, verify=False)
        if not r.status_code == requests.codes.ok:
            LOGGER.error("Can't access API")
            return
        features = r.json()['result']

        return json.dumps(features)

    @classmethod
    def source_name(cls):
        return 'PetaBencana'

    @classmethod
    def source_key(cls):
        return 'petabencana'

    @classmethod
    def region_name(cls):
        return 'Jakarta'
