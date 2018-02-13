# coding=utf-8
import logging
import os
import shutil
import unittest
from datetime import datetime

import pytz
import requests
from dateutil.parser import parse

from realtime import settings
from realtime.ash.ash_hazard import AshHazard
from realtime.ash.process_events import process_event
from realtime.settings import ON_TRAVIS
from realtime.tests.mock_server import InaSAFEDjangoMockServerHandler, \
    InaSAFEDjangoMockServer
from realtime.utilities import realtime_logger_name
from safe.test.qgis_app import qgis_app
from safe.utilities.keyword_io import KeywordIO

APP, IFACE = qgis_app()
LOGGER = logging.getLogger(realtime_logger_name())


class TestAshHazard(unittest.TestCase):

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

    def test_ash_fall_conversion(self):
        """Test GeoTIFF conversion to InaSAFE Hazard Layer."""
        time_zone = pytz.timezone('Asia/Jakarta')
        event_time = datetime(2017, 02, 21, 12, 04, tzinfo=pytz.utc)
        event_time = event_time.astimezone(time_zone)
        ash_hazard = AshHazard(
            event_time=event_time,
            ash_file_path=self.fixture_path(
                '201702211204+0000_Merapi-hazard.tif'),
            volcano_name='Merapi',
            region='Magelang',
            latitude=110.444,
            longitude=-7.575,
            alert_level='Normal',
            eruption_height=100,
            vent_height=2968,
            forecast_duration=3,
            output_dir=self.output_dir)

        self.assertTrue(ash_hazard.hazard_exists)

        expected_data = {
            'ash_id': '201702211904+0700_Merapi',
            'event_time': '2017-02-21 19:04:00+07:00',
            'time_zone': 'Asia/Jakarta',
            'eruption_height': 100,
            'eruption_height_asl': 3068,
            'vent_height': 2968,
            'volcano_name': 'Merapi',
            'region': 'Magelang',
            'latitude': 110.444,
            'longitude': -7.575,
            'alert_level': 'Normal',
            'forecast_duration': 3
        }

        actual_data = {
            'ash_id': ash_hazard.ash_id,
            'event_time': str(ash_hazard.event_time),
            'time_zone': str(ash_hazard.time_zone),
            'eruption_height': ash_hazard.eruption_height,
            'eruption_height_asl': ash_hazard.eruption_height_asl,
            'vent_height': ash_hazard.vent_height,
            'volcano_name': ash_hazard.volcano_name,
            'region': ash_hazard.region,
            'latitude': ash_hazard.latitude,
            'longitude': ash_hazard.longitude,
            'alert_level': ash_hazard.alert_level,
            'forecast_duration': ash_hazard.forecast_duration
        }

        self.assertDictEqual(expected_data, actual_data)

        self.assertTrue(ash_hazard.is_valid())

        keywords_io = KeywordIO()

        actual_keywords = keywords_io.read_keywords(ash_hazard.hazard_layer)

        expected_keywords = {
            'active_band': 1,
            'hazard': 'volcanic_ash',
            'hazard_category': 'single_event',
            'keyword_version': '4.3',
            'layer_geometry': 'raster',
            'layer_mode': 'continuous',
            'layer_purpose': 'hazard',
            'title': '201702211904+0700_Merapi',
        }

        self.assertDictContainsSubset(expected_keywords, actual_keywords)

        # Check extra keywords
        actual_keywords = keywords_io.read_keywords(
            ash_hazard.hazard_layer, 'extra_keywords')

        expected_keywords = {
            u'volcano_name': u'Merapi',
            u'region': u'Magelang',
            u'volcano_alert_level': u'Normal',
            u'time_zone': u'Asia/Jakarta',
            u'volcano_latitude': u'110.444',
            u'volcano_longitude': u'-7.575',
            u'volcano_event_id': u'201702211904+0700_Merapi',
            u'volcano_eruption_event_time': u'2017-02-21 19:04:00+07:00',
            u'volcano_eruption_height': u'100',
            u'volcano_height': u'2968',
            u'volcano_forecast_duration': u'3'
        }

        self.assertDictEqual(expected_keywords, actual_keywords)

    def test_process_event(self):
        """Test process event executions from hazard file."""

        # Set Up handler
        test_instance = self
        test_instance.rest_errors = 0

        time_zone = pytz.timezone('Asia/Jakarta')
        event_time = datetime(2017, 02, 21, 12, 04, tzinfo=pytz.utc)
        event_time = event_time.astimezone(time_zone)

        class ProcessEventCheckHandler(InaSAFEDjangoMockServerHandler):

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
                    suffix = '/realtime/api/v1/ash/Merapi/20170221190400+0700/'
                    if self.path.endswith(suffix):
                        self.logger_PUT()
                        # Check Ash hazard put
                        body_dict = self.parse_request_body()

                        expected_value = {
                            'volcano_name': 'Merapi',
                            'event_time': str(event_time),
                            'hazard_path': '/home/app/realtime/ash/tests/'
                                           'output/201702211904+0700_Merapi/'
                                           'ash_fall.tif'
                        }
                        test_instance.assertDictEqual(
                            body_dict, expected_value)

                        # test parse datetime
                        test_instance.assertEqual(
                            parse(body_dict['event_time']),
                            event_time)
                        self.send_response(requests.codes.ok)
                        self.end_headers()
                    else:
                        return InaSAFEDjangoMockServerHandler.do_PUT(self)
                except BaseException:
                    test_instance.rest_errors += 1
                    raise

        self.mock_server = InaSAFEDjangoMockServer(
            self.mock_host, self.mock_port, ProcessEventCheckHandler)
        self.mock_server.start_server()

        ret_val = process_event(
            working_dir=self.output_dir,
            ash_file_path=self.fixture_path(
                '201702211204+0000_Merapi-hazard.tif'),
            volcano_name='Merapi',
            region='Magelang',
            latitude=110.444,
            longitude=-7.575,
            alert_level='Normal',
            event_time=event_time,
            eruption_height=100,
            vent_height=2968,
            forecast_duration=3)

        self.assertTrue(ret_val)
        self.assertTrue(test_instance.rest_errors == 0)
