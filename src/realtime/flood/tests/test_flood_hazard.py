# coding=utf-8
import json
import logging
import os
import shutil
import unittest
from datetime import datetime

import mock
import pytz
import requests
from dateutil.parser import parse

from realtime import settings
from realtime.flood.data_source import DATA_SOURCE_DICT
from realtime.flood.flood_hazard import FloodHazard
from realtime.flood.process_events import process_event
from realtime.settings import ON_TRAVIS
from realtime.tests.mock_server import InaSAFEDjangoMockServerHandler, \
    InaSAFEDjangoMockServer
from realtime.utilities import realtime_logger_name
from safe.test.qgis_app import qgis_app
from safe.utilities.keyword_io import KeywordIO

APP, IFACE = qgis_app()
LOGGER = logging.getLogger(realtime_logger_name())


class TestFloodHazard(unittest.TestCase):

    def fixture_path(self, *path):
        current_dir = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(current_dir, 'fixtures', *path))

    def setUp(self):
        self.output_dir = self.fixture_path('../output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # mock url
        self.inasafe_django_rest_url = settings.INASAFE_REALTIME_REST_URL
        self.mock_host = 'localhost'
        self.mock_port = 8000
        settings.INASAFE_REALTIME_REST_URL = (
            'http://{host}:{port}/realtime/api/v1').format(
            host=self.mock_host, port=self.mock_port)

        # Configure Mock Server
        self.mock_server = None

    def tearDown(self):
        if ON_TRAVIS:
            try:
                shutil.rmtree(self.output_dir)
            except BaseException:
                pass

        # restore url
        settings.INASAFE_REALTIME_REST_URL = self.inasafe_django_rest_url

        # shutdown mock server
        if self.mock_server:
            self.mock_server.shutdown()

    def test_geojson_conversion(self):
        """Test GeoJSON conversion to InaSAFE Hazard Layer."""
        time_zone = pytz.timezone('Asia/Jakarta')
        data_source = DATA_SOURCE_DICT['petabencana']
        flood_hazard = FloodHazard(
            event_time=datetime(2017, 02, 21, 05, tzinfo=pytz.utc),
            time_zone=time_zone,
            duration=6,
            level='rw',
            geojson_file_path=self.fixture_path('flood_data.json'),
            data_source=data_source,
            output_dir=self.output_dir)

        self.assertTrue(flood_hazard.hazard_exists)

        expected_data = {
            'flood_id': '2017022105-6-rw',
            'event_time': '2017-02-21 05:00:00+00:00',
            'time_zone': 'Asia/Jakarta',
            'duration': 6,
            'level': 'rw',
            'event_time_in_time_zone': '2017-02-21 12:00:00+07:00',
        }

        actual_data = {
            'flood_id': flood_hazard.flood_id,
            'event_time': str(flood_hazard.event_time),
            'time_zone': str(flood_hazard.time_zone),
            'duration': flood_hazard.duration,
            'level': flood_hazard.level,
            'event_time_in_time_zone': str(
                flood_hazard.event_time_in_time_zone)
        }

        self.assertDictEqual(expected_data, actual_data)

        self.assertTrue(flood_hazard.is_valid())

        expected_keywords = {
            'layer_purpose': 'hazard',
            'hazard': 'flood',
            'hazard_category': 'single_event',
            'keyword_version': '4.4',
            'title': 'Jakarta Floods - 2017-02-21 12:00:00+07:00',
            'source': 'PetaBencana'
        }

        keywords_io = KeywordIO()

        actual_keywords = keywords_io.read_keywords(flood_hazard.hazard_layer)

        self.assertDictContainsSubset(expected_keywords, actual_keywords)

        expected_extra_keywords = {
            u'flood_event_time': u'2017-02-21T05:00:00',
            u'flood_event_id': u'2017022105-6-rw',
            u'time_zone': u'Asia/Jakarta'
        }

        extra_keywords = actual_keywords['extra_keywords']
        self.assertDictEqual(expected_extra_keywords, extra_keywords)

    def test_process_event_file(self):
        """Test process event executions from hazard file."""

        # Set up handler
        test_instance = self
        test_instance.rest_errors = 0

        class ProcessCheckHandler(InaSAFEDjangoMockServerHandler):

            def do_GET(self):
                if self.path.endswith('/realtime/api/v1/auth/login/'):
                    self.logger_GET()
                    # Check login
                    self.send_response(requests.codes.ok)
                    self.send_header('Set-Cookie', 'csrftoken=thisisatoken')
                    self.end_headers()
                else:
                    return InaSAFEDjangoMockServerHandler.do_GET(self)

            def do_POST(self):
                try:
                    if self.path.endswith('/realtime/api/v1/auth/login/'):
                        self.logger_POST()
                        # Check login validation
                        body_dict = self.parse_request_body()
                        expected_value = {
                            'username': 'test@realtime.inasafe.org',
                            'password': 'thepaassword',
                            'csrfmiddlewaretoken': 'thisisatoken'
                        }
                        test_instance.assertDictContainsSubset(
                            expected_value, body_dict)
                        self.send_response(requests.codes.ok)
                        self.end_headers()
                    else:
                        return InaSAFEDjangoMockServerHandler.do_POST(self)
                except BaseException:
                    test_instance.rest_errors += 1
                    raise

            def do_PUT(self):
                try:
                    if self.path.endswith(
                            '/realtime/api/v1/flood/2017022105-6-rw/'):
                        # Check flood put
                        self.logger_PUT()
                        body_dict = self.parse_request_body()
                        expected_value = {
                            'data_source': 'Hazard File',
                            'event_id': '2017022105-6-rw',
                            'region': 'Jakarta',
                            'interval': '6',
                            'source': 'hazard_file',
                            'time': '2017-02-21 05:00:00+00:00',
                            'hazard_path': '/home/app/realtime/'
                                           'flood/tests/output/'
                                           '2017022105-6-rw/flood_data.json'
                        }
                        test_instance.assertDictContainsSubset(
                            expected_value, body_dict)
                        self.send_response(requests.codes.ok)
                        self.end_headers()
                    else:
                        return InaSAFEDjangoMockServerHandler.do_PUT(self)
                except BaseException:
                    test_instance.rest_errors += 1
                    raise

        self.mock_server = InaSAFEDjangoMockServer(
            self.mock_host, self.mock_port, ProcessCheckHandler)
        self.mock_server.start_server()

        ret_val = process_event(
            working_dir=self.output_dir,
            flood_id='2017022105-6-rw',
            time_zone=pytz.timezone('Asia/Jakarta'),
            data_source='hazard_file',
            data_source_args={
                'filename': self.fixture_path('flood_data.json')
            })

        self.assertTrue(ret_val)
        self.assertTrue(test_instance.rest_errors == 0)

    def test_process_event_petabencana(self):
        """Test process event executions from mocked PetaBencana API."""
        # Set up handler
        test_instance = self
        test_instance.rest_errors = 0

        event_time = datetime.utcnow().replace(tzinfo=pytz.utc)

        event_id = '{time:%Y%m%d%H}-6-rw'.format(time=event_time)
        LOGGER.info('Event ID: {0}'.format(event_id))

        class ProcessCheckHandler(InaSAFEDjangoMockServerHandler):

            def do_GET(self):
                if self.path.endswith('/realtime/api/v1/auth/login/'):
                    self.logger_GET()
                    # Check login
                    self.send_response(requests.codes.ok)
                    self.send_header('Set-Cookie', 'csrftoken=thisisatoken')
                    self.end_headers()
                else:
                    return InaSAFEDjangoMockServerHandler.do_GET(self)

            def do_POST(self):
                try:
                    if self.path.endswith('/realtime/api/v1/auth/login/'):
                        self.logger_POST()
                        # Check login validation
                        body_dict = self.parse_request_body()
                        expected_value = {
                            'username': 'test@realtime.inasafe.org',
                            'password': 'thepaassword',
                            'csrfmiddlewaretoken': 'thisisatoken'
                        }
                        test_instance.assertDictContainsSubset(
                            expected_value, body_dict)
                        self.send_response(requests.codes.ok)
                        self.end_headers()
                    else:
                        return InaSAFEDjangoMockServerHandler.do_POST(self)
                except BaseException:
                    test_instance.rest_errors += 1
                    raise

            def do_PUT(self):
                try:
                    if self.path.endswith(
                            '/realtime/api/v1/flood/{event_id}/'.format(
                                event_id=event_id)):
                        # Check flood put
                        self.logger_PUT()
                        body_dict = self.parse_request_body()
                        expected_value = {
                            'data_source': 'PetaBencana',
                            'event_id': event_id,
                            'region': 'Jakarta',
                            'interval': '6',
                            'source': 'petabencana',
                            'hazard_path': (
                                '/home/app/realtime/'
                                'flood/tests/output/'
                                '{event_id}/'
                                'flood_data.json').format(
                                event_id=event_id)
                        }
                        test_instance.assertDictContainsSubset(
                            expected_value, body_dict)
                        # compare time because it may have different seconds
                        seconds_diff = (
                                parse(body_dict['time']) - event_time).seconds
                        test_instance.assertTrue(seconds_diff < 60)
                        self.send_response(requests.codes.ok)
                        self.end_headers()
                    else:
                        return InaSAFEDjangoMockServerHandler.do_PUT(self)
                except BaseException:
                    test_instance.rest_errors += 1
                    raise

        self.mock_server = InaSAFEDjangoMockServer(
            self.mock_host, self.mock_port, ProcessCheckHandler)
        self.mock_server.start_server()

        # patch mock response
        # We are using python requests, so we can mock the
        # requests object.
        with mock.patch('requests.get') as get_mock:
            get_mock.return_value = mock_response = mock.Mock()
            mock_response.status_code = 200

            def mock_json():
                with open(self.fixture_path('flood_data.json')) as f:
                    geojson_result = f.read()
                geojson_object = json.loads(geojson_result)
                return {
                    'result': geojson_object
                }
            mock_response.json = mock_json

            # begin testing
            ret_val = process_event(
                working_dir=self.output_dir,
                time_zone=pytz.timezone('Asia/Jakarta'),
                data_source='petabencana',
                data_source_args={
                    'duration': 6,
                    'level': 'rw'
                })

        self.assertTrue(ret_val)
        self.assertTrue(test_instance.rest_errors == 0)
