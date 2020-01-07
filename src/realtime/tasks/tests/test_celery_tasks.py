# coding=utf-8
import json
import os
import shutil
import unittest
from datetime import datetime

import mock
import pytz
from qgis.core import QgsMapLayerRegistry

from realtime import settings
from realtime.celeryconfig import task_always_eager
from realtime.tasks.ash import process_ash
from realtime.tasks.earthquake import process_shake
from realtime.tasks.flood import process_flood
from realtime.tasks.generic import check_broker_connection
from realtime.tests.mock_server import InaSAFEDjangoMockServerHandler, \
    InaSAFEDjangoMockServer
from realtime.utilities import copy_layers
from safe.test.qgis_app import qgis_app

APP, IFACE = qgis_app()


class TestGenericCeleryTasks(unittest.TestCase):

    def test_broker_connection(self):
        """Test broker connection check."""

        result = check_broker_connection.delay()

        self.assertTrue(result.get())


class TestEarthquakeCeleryTasks(unittest.TestCase):

    def check_layer_registry_empty(self):
        # Layer registry should be empty between run
        layer_registry = QgsMapLayerRegistry.instance()
        self.assertDictEqual(layer_registry.mapLayers(), {})

    def setUp(self):
        self.shake_work_dir = settings.EARTHQUAKE_WORKING_DIRECTORY
        self.event_id = '20161214005704'
        self.grid_file_path = os.path.join(
            self.shake_work_dir, '20161214005704/grid.xml')
        try:
            os.makedirs(os.path.dirname(self.grid_file_path))
        except OSError:
            pass
        shutil.copy(self.shake_fixtures_path('grid.xml'), self.grid_file_path)

        # mock url
        self.inasafe_django_rest_url = settings.INASAFE_REALTIME_REST_URL
        self.mock_host = 'localhost'
        self.mock_port = 8000
        settings.INASAFE_REALTIME_REST_URL = (
            'http://{host}:{port}/realtime/api/v1').format(
            host=self.mock_host, port=self.mock_port)

        # Configure Mock Server
        self.mock_server = InaSAFEDjangoMockServer(
            self.mock_host, self.mock_port, InaSAFEDjangoMockServerHandler)
        self.mock_server.start_server()

    def tearDown(self):
        if settings.ON_TRAVIS:
            try:
                shutil.rmtree(os.path.dirname(self.grid_file_path))
            except OSError:
                pass

        # restore url
        settings.INASAFE_REALTIME_REST_URL = self.inasafe_django_rest_url

        # shutdown mock server
        self.mock_server.shutdown()

    @staticmethod
    def shake_fixtures_path(*path):
        current_dir = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(
            current_dir, '../../earthquake/tests/fixtures', *path))

    def test_process_shake(self):
        """Test processing shake file from celery task request."""
        result = process_shake.delay(self.event_id, self.grid_file_path)
        self.assertTrue(result.get()['success'])

        self.check_layer_registry_empty()


class TestFloodCeleryTasks(unittest.TestCase):

    def check_layer_registry_empty(self):
        # Layer registry should be empty between run
        layer_registry = QgsMapLayerRegistry.instance()
        self.assertDictEqual(layer_registry.mapLayers(), {})

    def setUp(self):
        self.flood_work_dir = settings.FLOOD_WORKING_DIRECTORY
        self.event_id = '2017022105-6-rw'
        self.flood_output_dir = os.path.join(
            self.flood_work_dir, self.event_id)
        self.flood_hazard_file = os.path.join(
            self.flood_output_dir, 'flood_data.json')

        # mock url
        self.inasafe_django_rest_url = settings.INASAFE_REALTIME_REST_URL
        self.mock_host = 'localhost'
        self.mock_port = 8000
        settings.INASAFE_REALTIME_REST_URL = (
            'http://{host}:{port}/realtime/api/v1').format(
            host=self.mock_host, port=self.mock_port)

        # Configure Mock Server
        self.mock_server = InaSAFEDjangoMockServer(
            self.mock_host, self.mock_port, InaSAFEDjangoMockServerHandler)
        self.mock_server.start_server()

    def tearDown(self):
        if settings.ON_TRAVIS:
            try:
                shutil.rmtree(self.flood_output_dir)
            except OSError:
                pass

        # restore url
        settings.INASAFE_REALTIME_REST_URL = self.inasafe_django_rest_url

        # shutdown mock server
        self.mock_server.shutdown()

    @staticmethod
    def flood_fixtures_path(*path):
        current_dir = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(
            current_dir, '../../flood/tests/fixtures', *path))

    def test_process_event_file(self):
        """Test celery executions for hazard file."""

        # First, emulate file copy into a target directory

        try:
            os.makedirs(self.flood_output_dir)
        except OSError:
            pass

        shutil.copy(
            self.flood_fixtures_path('flood_data.json'),
            self.flood_hazard_file)

        # Second, initiate request to process hazard file.

        result = process_flood.delay(
            flood_id=self.event_id,
            time_zone=pytz.timezone('Asia/Jakarta'),
            data_source='hazard_file',
            data_source_args={
                'filename': self.flood_hazard_file
            })
        self.assertTrue(result.get()['success'])

        self.check_layer_registry_empty()

    @unittest.skipIf(
        not task_always_eager,
        'Only run this tests synchronously. '
        'Because it needs a patched PetaBencana REST API.')
    def test_process_event_petabencana(self):
        """Test celery executions for petabencana hazard source."""

        # patch mock response
        # We are using python requests, so we can mock the
        # requests object.
        with mock.patch('requests.get') as get_mock:
            get_mock.return_value = mock_response = mock.Mock()
            mock_response.status_code = 200

            def mock_json():
                with open(self.flood_fixtures_path('flood_data.json')) as f:
                    geojson_result = f.read()
                geojson_object = json.loads(geojson_result)
                return {
                    'result': geojson_object
                }

            mock_response.json = mock_json

            # begin sending celery task using default argument
            result = process_flood.delay()
            self.assertTrue(result.get()['success'])

            self.check_layer_registry_empty()


class TestAshCeleryTasks(unittest.TestCase):

    def check_layer_registry_empty(self):
        # Layer registry should be empty between run
        layer_registry = QgsMapLayerRegistry.instance()
        self.assertDictEqual(layer_registry.mapLayers(), {})

    def setUp(self):
        self.ash_work_dir = settings.ASH_WORKING_DIRECTORY
        self.event_id = '201702211204+0000_Merapi'
        self.ash_output_dir = os.path.join(
            self.ash_work_dir, self.event_id)
        self.ash_hazard_file = os.path.join(
            self.ash_output_dir, 'ash_fall.tif')

        # mock url
        self.inasafe_django_rest_url = settings.INASAFE_REALTIME_REST_URL
        self.mock_host = 'localhost'
        self.mock_port = 8000
        settings.INASAFE_REALTIME_REST_URL = (
            'http://{host}:{port}/realtime/api/v1').format(
            host=self.mock_host, port=self.mock_port)

        # Configure Mock Server
        self.mock_server = InaSAFEDjangoMockServer(
            self.mock_host, self.mock_port, InaSAFEDjangoMockServerHandler)
        self.mock_server.start_server()

    def tearDown(self):
        if settings.ON_TRAVIS:
            try:
                shutil.rmtree(self.ash_output_dir)
            except OSError:
                pass

        # restore url
        settings.INASAFE_REALTIME_REST_URL = self.inasafe_django_rest_url

        # shutdown mock server
        self.mock_server.shutdown()

    @staticmethod
    def ash_fixtures_path(*path):
        current_dir = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(
            current_dir, '../../ash/tests/fixtures', *path))

    def test_process_event_file(self):
        """Test celery executions for hazard file."""

        # First, emulate file copy into a target directory

        try:
            os.makedirs(self.ash_output_dir)
        except OSError:
            pass

        copy_layers(
            self.ash_fixtures_path('201702211204+0000_Merapi-hazard.tif'),
            self.ash_hazard_file)

        # Second, initiate request to process hazard file.

        time_zone = pytz.timezone('Asia/Jakarta')
        event_time = datetime(2017, 0o2, 21, 12, 0o4, tzinfo=pytz.utc)
        event_time = event_time.astimezone(time_zone)

        result = process_ash.delay(
            ash_file_path=self.ash_hazard_file,
            volcano_name='Merapi',
            region='Magelang',
            latitude=110.444,
            longitude=-7.575,
            alert_level='Normal',
            event_time=event_time,
            eruption_height=100,
            vent_height=2968,
            forecast_duration=3)
        self.assertTrue(result.get()['success'])

        self.check_layer_registry_empty()
