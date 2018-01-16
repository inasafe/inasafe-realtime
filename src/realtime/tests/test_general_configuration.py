# coding=utf-8
import unittest

from safe.test.qgis_app import qgis_app


class TestGeneralConfiguration(unittest.TestCase):

    def test_import_inasafe(self):
        """Test that Realtime properly run InaSAFE."""
        # Test import safe package
        import safe # noqa
        # Test instantiate QGIS instance
        APP, IFACE = qgis_app()
