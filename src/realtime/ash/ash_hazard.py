from builtins import str
# coding=utf-8
import logging
import os
from shutil import copy

from PyQt4.QtCore import QObject
from qgis.core import QgsRasterLayer

from realtime.ash.localizations import AshHazardString
from realtime.ash.settings import ASH_HAZARD_DEFAULT_BASENAME, ASH_ID_FORMAT
from realtime.utilities import realtime_logger_name, copy_layers
from safe.common.exceptions import NoKeywordsFoundError
from safe.definitions import (
    property_extra_keywords,
    layer_mode,
    layer_purpose,
    continuous_hazard_unit,
    layer_geometry,
    inasafe_keyword_version_key,
    hazard_category)
from safe.definitions.exposure import (
    exposure_structure,
    exposure_place,
    exposure_land_cover,
    exposure_road,
    exposure_population,
)
from safe.definitions.extra_keywords import (
    extra_keyword_volcano_name,
    extra_keyword_region,
    extra_keyword_volcano_alert_level,
    extra_keyword_time_zone,
    extra_keyword_volcano_latitude,
    extra_keyword_volcano_longitude,
    extra_keyword_volcano_event_id,
    extra_keyword_volcano_eruption_event_time,
    extra_keyword_eruption_height,
    extra_keyword_volcano_height,
    extra_keyword_volcano_forecast_duration,
)
from safe.definitions.hazard import hazard_volcanic_ash
from safe.definitions.hazard_category import hazard_category_single_event
from safe.definitions.hazard_classifications import ash_hazard_classes
from safe.definitions.layer_geometry import layer_geometry_raster
from safe.definitions.layer_modes import layer_mode_continuous
from safe.definitions.layer_purposes import layer_purpose_hazard
from safe.definitions.units import unit_centimetres
from safe.definitions.versions import inasafe_keyword_version
from safe.utilities.keyword_io import KeywordIO

LOGGER = logging.getLogger(realtime_logger_name())


class AshHazard(QObject):
    """Class placeholder for Flood hazard object."""

    def __init__(
            self, ash_file_path, volcano_name, region,
            latitude, longitude, alert_level,
            event_time, eruption_height, vent_height, forecast_duration,
            ash_id=None, output_dir=None, output_basename=None):
        """Create Ash hazard event placeholder object.

        :param ash_file_path: File path to ash layer
        :type ash_file_path: str

        :param volcano_name: The volcano name
        :type volcano_name: str

        :param region: The region where the volcano located
        :type region: str

        :param latitude: Latitude number in EPSG:4326
        :type latitude: float

        :param longitude: Longitude number in EPSG:4326
        :type longitude: float

        :param alert_level: Alert level string. Alailable value:
            Normal, Warning, Advisory, Watch
        :type alert_level: str

        :param event_time: Event time of Ash with timezone
        :type event_time: datetime.datetime

        :param eruption_height: Eruption height calculated from volcano height
            / vent height
        :type eruption_height: float

        :param vent_height: Height of volcano / Height of vent
        :type vent_height: float

        :param forecast_duration: Forecast duration of model in days
        :type forecast_duration: float

        :param ash_id: Ash ID
        :type ash_id: str

        :param output_dir: Optional argument to specify output directory of
            generated InaSAFE Layer
        :type output_dir: str

        :param output_basename: Optional argument to specify the basename of
            generated InaSAFE Layer
        """

        super(AshHazard, self).__init__()
        self.localization = AshHazardString()
        self._volcano_name = volcano_name
        self._region = region
        self._alert_level = alert_level
        self._event_time = event_time
        self._eruption_height = eruption_height
        self._vent_height = vent_height
        self._latitude = latitude
        self._longitude = longitude
        self._forecast_duration = forecast_duration

        if ash_id:
            self._ash_id = ash_id
        else:
            self._ash_id = ASH_ID_FORMAT.format(
                event_time=self.event_time,
                volcano_name=self.volcano_name)

        if not output_dir:
            output_dir = os.path.dirname(ash_file_path)

        if not output_basename:
            output_basename = ASH_HAZARD_DEFAULT_BASENAME

        ash_file = '{basename}.tif'.format(basename=output_basename)

        # QgsRaster can already read GeoTIFF
        # InaSAFE layer are able to process GeoTIFF
        self.hazard_path = os.path.join(output_dir, ash_file)

        if not ash_file_path == self.hazard_path:
            # Copy hazard file first
            copy_layers(ash_file_path, self.hazard_path)

        # Insert metadata and styles
        self.copy_style()
        self.write_keywords()

    @classmethod
    def resource_path(cls, *path):
        """Refer to hazard resource path."""
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                'resources',
                *path))

    def copy_style(self):
        """Copy style from the OSM resource directory to the output path.

        .. versionadded: 3.3

        """
        source_qml_path = self.resource_path('ash-style.qml')
        output_qml_path = self.hazard_path.replace('tif', 'qml')
        LOGGER.info('Copying qml to: {0}'.format(output_qml_path))
        copy(source_qml_path, output_qml_path)

    def write_keywords(self):
        keyword_io = KeywordIO()

        hazard_classes = {
            ash_hazard_classes['key']: {
                u'active': True,
                u'classes': {
                    u'high': [5.0, 10.0],
                    u'very high': [10.0, 9999.0],
                    u'very low': [0.01, 0.1],
                    u'medium': [2.0, 5.0],
                    u'low': [0.1, 2.0]
                }
            }
        }

        keywords = {
            'active_band': 1,
            hazard_category['key']: hazard_category_single_event['key'],
            'title': self.ash_id,
            'thresholds': {
                exposure_structure['key']: hazard_classes,
                exposure_place['key']: hazard_classes,
                exposure_land_cover['key']: hazard_classes,
                exposure_road['key']: hazard_classes,
                exposure_population['key']: hazard_classes
            },
            inasafe_keyword_version_key: inasafe_keyword_version,
            layer_purpose['key']: layer_purpose_hazard['key'],
            layer_purpose_hazard['key']: hazard_volcanic_ash['key'],
            continuous_hazard_unit['key']: unit_centimetres['key'],
            layer_geometry['key']: layer_geometry_raster['key'],
            layer_mode['key']: layer_mode_continuous['key'],
            property_extra_keywords['key']: {
                extra_keyword_volcano_name['key']: self.volcano_name,
                extra_keyword_region['key']: self.region,
                extra_keyword_volcano_alert_level['key']: self.alert_level,
                extra_keyword_time_zone['key']: str(self.time_zone),
                extra_keyword_volcano_latitude['key']: str(self.latitude),
                extra_keyword_volcano_longitude['key']: str(self.longitude),
                extra_keyword_volcano_event_id['key']: self.ash_id,
                extra_keyword_volcano_eruption_event_time['key']: str(
                    self.event_time),
                extra_keyword_eruption_height['key']: str(
                    self.eruption_height),
                extra_keyword_volcano_height['key']: str(self.vent_height),
                extra_keyword_volcano_forecast_duration['key']: str(
                    self.forecast_duration)
            }
        }

        hazard_layer = self.hazard_layer

        # check already assigned keywords
        current_keywords = {}
        try:
            current_keywords = keyword_io.read_keywords(self.hazard_layer)
        except (NoKeywordsFoundError, ValueError):
            # Create new if not any or failed to load
            pass
        current_keywords.update(keywords)
        keyword_io.write_keywords(self.hazard_layer, current_keywords)
        hazard_layer.setTitle(keywords['title'])

    @property
    def event_time(self):
        """Return event time in UTC"""
        return self._event_time

    @property
    def time_zone(self):
        """Return time zone of hazard"""
        return self.event_time.tzinfo

    @property
    def ash_id(self):
        """Return flood ID"""
        return self._ash_id

    @property
    def volcano_name(self):
        """Return volcano name"""
        return self._volcano_name

    @property
    def region(self):
        """Return volcano registered region"""
        return self._region

    @property
    def latitude(self):
        """Return volcano latitude coordinate"""
        return self._latitude

    @property
    def longitude(self):
        """Return volcano longitude coordinate"""
        return self._longitude

    @property
    def alert_level(self):
        """Return alert level"""
        return self._alert_level

    @property
    def eruption_height(self):
        """Return height of eruption, calculated from vent height."""
        return self._eruption_height

    @property
    def vent_height(self):
        """Return height of vent, calculated from above sea level."""
        return self._vent_height

    @property
    def forecast_duration(self):
        """Return Forecast Duration of model in days"""
        return self._forecast_duration

    @property
    def eruption_height_asl(self):
        """Return height of eruption, calculated from above sea level."""
        return self.vent_height + self.eruption_height

    @property
    def hazard_exists(self):
        """Make sure hazard layer generated
        :return: True if hazard exists
        :rtype: bool
        """
        # Perform other checks to make sure hazard file is complete
        return os.path.exists(self.hazard_path)

    @property
    def hazard_layer(self):
        """
        :return: QGIS Layer of Hazard file
        :rtype: QgsRasterLayer
        """
        return QgsRasterLayer(self.hazard_path)

    def is_valid(self):
        """Validate InaSAFE Layer generation."""
        if self.hazard_exists and self.hazard_layer.isValid():
            return True
        return False
