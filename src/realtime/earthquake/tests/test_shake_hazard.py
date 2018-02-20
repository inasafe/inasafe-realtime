# coding=utf-8
import datetime
import logging
import os
import shutil
import unittest

import pytz
import requests

from realtime import settings
from realtime.earthquake.process_event import process_event
from realtime.earthquake.settings import EQ_GRID_ALGORITHM
from realtime.earthquake.shake_hazard import ShakeHazard
from realtime.settings import ON_TRAVIS, INASAFE_REALTIME_DATETIME_FORMAT
from realtime.tests.mock_server import InaSAFEDjangoMockServer, \
    InaSAFEDjangoMockServerHandler
from realtime.utilities import realtime_logger_name
from safe.test.qgis_app import qgis_app
from safe.utilities.keyword_io import KeywordIO

APP, IFACE = qgis_app()
LOGGER = logging.getLogger(realtime_logger_name())


class TestShakeHazard(unittest.TestCase):

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

    def test_grid_conversion(self):
        """Test Shake Grid conversion to InaSAFE Hazard Layer."""
        shake_hazard = ShakeHazard(
            grid_file=self.fixture_path('grid.xml'),
            force_flag=True,
            algorithm=EQ_GRID_ALGORITHM,
            output_dir=self.output_dir)

        self.assertTrue(shake_hazard.hazard_exists)

        expected_data = {
            'depth': 3.0,
            'event_id': u'20161214005704',
            'hazard_path': '/home/app/realtime/earthquake/tests/'
                           'output/hazard-use_ascii.tif',
            'latitude': 4.92,
            'longitude': 96.55,
            'magnitude': 3.5,
            'source': 'BMKG (Badan Meteorologi, Klimatologi, dan Geofisika) '
                      'Indonesia',
            'source_type': 'initial',
            'time_zone': 'Asia/Jakarta',
            'timestamp': '2016-12-14 00:57:04+07:00'
        }

        actual_data = {
            'depth': shake_hazard.depth,
            'event_id': shake_hazard.event_id,
            'hazard_path': shake_hazard.hazard_path,
            'latitude': shake_hazard.latitude,
            'longitude': shake_hazard.longitude,
            'magnitude': shake_hazard.magnitude,
            'source': shake_hazard.source,
            'source_type': shake_hazard.source_type,
            'time_zone': shake_hazard.time_zone,
            'timestamp': str(shake_hazard.timestamp)
        }

        self.assertDictEqual(expected_data, actual_data)

        self.assertTrue(shake_hazard.is_valid())

        expected_extra_keywords = {
            u'earthquake_event_id': u'20161214005704',
            u'earthquake_magnitude': 3.5,
            u'time_zone': u'Asia/Jakarta',
            u'earthquake_longitude': 96.55,
            u'earthquake_x_maximum': 97.8,
            u'earthquake_y_minimum': 3.675,
            u'earthquake_location': u'Aceh',
            u'earthquake_x_minimum': 95.3,
            u'earthquake_latitude': 4.92,
            u'earthquake_y_maximum': 6.165,
            u'earthquake_depth': 3.0,
            u'earthquake_event_time': u'2016-12-14T00:57:04'
        }

        keywords_io = KeywordIO()

        actual_extra_keywords = keywords_io.read_keywords(
            shake_hazard.hazard_layer, keyword='extra_keywords')

        self.assertDictEqual(expected_extra_keywords, actual_extra_keywords)

    def test_process_event(self):
        """Test process event executions."""

        test_instance = self
        test_instance.rest_errors = 0

        time_zone = pytz.timezone('Asia/Jakarta')
        event_time = datetime.datetime(2016, 12, 14, 00, 57, 04)
        event_time = time_zone.localize(event_time)

        # Make sure timezone correction is, well, *correct*
        self.assertEqual(str(event_time), '2016-12-14 00:57:04+07:00')

        class ProcessEventCheckHandler(InaSAFEDjangoMockServerHandler):

            def do_GET(self):
                if self.path.endswith('/realtime/api/v1/auth/login/'):
                    self.logger_GET()
                    # Check login
                    self.send_response(requests.codes.ok)
                    self.send_header('Set-Cookie', 'csrftoken=thisisatoken')
                    self.end_headers()
                elif self.path.endswith('/realtime/api/v1/is_logged_in/'):
                    self.logger_GET()
                    # Validate login
                    self.send_response(requests.codes.ok)
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
                    elif self.path.endswith(
                            '/realtime/api/v1/'
                            'indicator/notify_shakemap_push/'):
                        self.logger_POST()
                        body_dict = self.parse_request_body()
                        expected_value = {
                            'timestamp': event_time.astimezone(
                                pytz.utc).strftime(
                                INASAFE_REALTIME_DATETIME_FORMAT)
                        }
                        test_instance.assertDictEqual(
                            expected_value, body_dict)

                        expected_headers = {
                            'X-CSRFTOKEN': 'thisisatoken'
                        }

                        test_instance.assertDictContainsSubset(
                            expected_headers, self.headers)
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
                            '/realtime/api/v1/earthquake/'
                            '20161214005704/initial/'):
                        # Check shake put
                        self.logger_PUT()
                        body_dict = self.parse_request_body()

                        # Checkt attempt to update data
                        if 'shake_id' in body_dict:

                            expected_value = {
                                'shake_id': '20161214005704',
                                'location_description': 'Aceh',
                                'source_type': 'initial',
                                'depth': 3.0,
                                'magnitude': 3.5,
                                'location': {
                                    'type': 'Point',
                                    'coordinates': [96.55, 4.92]
                                },
                                'time': '2016-12-14 00:57:04+07:00',
                                'hazard_path': '/home/app/realtime/'
                                               'earthquake/tests/'
                                               'output/hazard-use_ascii.tif'
                            }
                            test_instance.assertEqual(
                                expected_value, body_dict)

                        # Check attempt to upload shake grid
                        elif 'shake_grid' in body_dict:

                            grid_xml_path = test_instance.fixture_path(
                                'grid.xml')

                            with open(grid_xml_path) as f:
                                shake_grid_xml = f.read()

                            # shake_grid file will be uploaded as multipart
                            # data. So in this case, parsed as string
                            expected_value = {
                                'shake_grid': [shake_grid_xml]
                            }

                            test_instance.assertEqual(
                                expected_value, body_dict)

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
            shake_id='{time:%Y%m%d%H%M%S}'.format(time=event_time),
            grid_file=self.fixture_path('grid.xml'),
            output_dir=self.output_dir)

        self.assertTrue(ret_val)
        self.assertTrue(test_instance.rest_errors == 0)
