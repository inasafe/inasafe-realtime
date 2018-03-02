# coding=utf-8
import logging
import os
from shutil import copy

from PyQt4.QtCore import QObject
from qgis.core import QgsVectorLayer

from realtime.flood.localizations import FloodHazardString
from realtime.flood.settings import (
    FLOOD_HAZARD_DEFAULT_BASENAME,
    FLOOD_ID_FORMAT)
from realtime.utilities import realtime_logger_name
from safe.definitions import (
    extra_keyword_flood_event_time,
    extra_keyword_flood_event_id,
    extra_keyword_time_zone,
    hazard_category,
    inasafe_keyword_version_key,
    layer_purpose,
    layer_geometry,
    layer_mode,
    property_extra_keywords)
from safe.definitions.exposure import (
    exposure_structure,
    exposure_place,
    exposure_land_cover,
    exposure_road,
    exposure_population
)
from safe.definitions.fields import hazard_value_field
from safe.definitions.hazard import hazard_flood
from safe.definitions.hazard_category import hazard_category_single_event
from safe.definitions.hazard_classifications import (
    flood_hazard_classes,
    flood_petabencana_hazard_classes
)
from safe.definitions.layer_geometry import layer_geometry_polygon
from safe.definitions.layer_modes import layer_mode_classified
from safe.definitions.layer_purposes import layer_purpose_hazard
from safe.definitions.versions import inasafe_keyword_version
from safe.utilities.keyword_io import KeywordIO

LOGGER = logging.getLogger(realtime_logger_name())


class FloodHazard(QObject):
    """Class placeholder for Flood hazard object."""

    def __init__(
            self, event_time, time_zone, duration, level,
            geojson_file_path, data_source,
            flood_id=None, output_dir=None, output_basename=None):
        """Create Flood hazard event placeholder object.

        :param flood_id: Flood ID
        :type flood_id: str

        :param event_time: Event time of Flood in UTC
        :type event_time: datetime.datetime

        :param time_zone: Timezone of Flood Hazard
        :type time_zone: pytz.tzinfo.DstTzInfo

        :param duration: Aggregate duration of flood
        :type duration: int

        :param level: Aggregation level of flood hazard
        :type level: str

        :param geojson_file_path: The path of hazard file (GeoJSON)
        :type geojson_file_path: str

        :param data_source: The source object of this hazard data
        :type data_source: realtime.flood.data_source.flood_data_source.
            FloodHazardBaseClassAPI

        :param output_dir: Optional argument to specify output directory of
            generated InaSAFE Layer
        :type output_dir: str

        :param output_basename: Optional argument to specify the basename of
            generated InaSAFE Layer
        """

        super(FloodHazard, self).__init__()
        self.localization = FloodHazardString()
        self._event_time = event_time
        self._time_zone = time_zone
        self._duration = duration
        self._level = level
        self._data_source = data_source

        if flood_id:
            self._flood_id = flood_id
        else:
            self._flood_id = FLOOD_ID_FORMAT.format(
                event_time=self.event_time,
                duration=self.duration,
                level=self.level)
        self._hazard_features = 0

        if not output_dir:
            output_dir = os.path.dirname(geojson_file_path)

        if not output_basename:
            output_basename = FLOOD_HAZARD_DEFAULT_BASENAME

        geojson_file = '{basename}.json'.format(basename=output_basename)

        # QgsVector can already read GeoJSON
        # InaSAFE layer are able to process GeoJSON
        self.hazard_path = os.path.join(output_dir, geojson_file)

        if not geojson_file_path == self.hazard_path:
            # Copy Hazard file first
            copy(geojson_file_path, self.hazard_path)

        # Insert metadata
        self.copy_style()
        self.write_keywords()

        # Calculate potential hazard features
        self.calculate_hazard_features()

    @classmethod
    def resource_path(cls, *path):
        """Refer to hazard resource path."""
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                'resources',
                *path))

    def copy_style(self):
        source_qml_path = self.resource_path('flood-style.qml')
        output_qml_path = self.hazard_path.replace('json', 'qml')
        LOGGER.info('Copying qml to: {0}'.format(output_qml_path))
        copy(source_qml_path, output_qml_path)

    def write_keywords(self):
        keyword_io = KeywordIO()

        hazard_classes = {
            flood_hazard_classes['key']: {
                u'active': False,
                u'classes': {
                    u'dry': [0, 1],
                    u'wet': [2, 3, 4]
                }
            },
            flood_petabencana_hazard_classes['key']: {
                u'active': True,
                u'classes': {
                    u'high': [4],
                    u'medium': [3],
                    u'low': [2],
                    u'use_caution': [1],
                }
            },
        }

        keywords = {
            hazard_category['key']: hazard_category_single_event['key'],
            'title': self.localization.hazard_title.format(
                timestamp=self.event_time_in_time_zone),
            inasafe_keyword_version_key: inasafe_keyword_version,
            'value_maps': {
                exposure_structure['key']: hazard_classes,
                exposure_place['key']:  hazard_classes,
                exposure_land_cover['key']:  hazard_classes,
                exposure_road['key']:  hazard_classes,
                exposure_population['key']:  hazard_classes,
            },
            layer_purpose['key']: layer_purpose_hazard['key'],
            layer_purpose_hazard['key']: hazard_flood['key'],
            'source': self.data_source.source_name(),
            layer_geometry['key']: layer_geometry_polygon['key'],
            'inasafe_fields': {hazard_value_field['key']: u'state'},
            layer_mode['key']: layer_mode_classified['key'],

            # Extra keywords
            property_extra_keywords['key']: {
                extra_keyword_flood_event_time['key']: self.event_time.strftime(
                    extra_keyword_flood_event_time['store_format2']),
                extra_keyword_flood_event_id['key']: self.flood_id,
                extra_keyword_time_zone['key']: (
                    self.time_zone.zone if self.time_zone else '')
            }
        }

        hazard_layer = self.hazard_layer
        keyword_io.write_keywords(self.hazard_layer, keywords)
        hazard_layer.setTitle(keywords['title'])

    @property
    def event_time(self):
        """Return event time in UTC"""
        return self._event_time

    @property
    def time_zone(self):
        """Return time zone of hazard"""
        return self._time_zone

    @property
    def flood_id(self):
        """Return flood ID"""
        return self._flood_id

    @property
    def duration(self):
        """Return aggregate duration of hazard"""
        return self._duration

    @property
    def level(self):
        """Return aggregation level of hazard"""
        return self._level

    @property
    def data_source(self):
        """Return the source of this hazard data"""
        return self._data_source

    @property
    def data_source_name(self):
        """Return the source name of this hazard data source"""
        return self._data_source.source_name()

    @property
    def event_time_in_time_zone(self):
        """Return event time in hazard time zone"""
        return self.event_time.astimezone(self._time_zone)

    @property
    def impacted_hazard_features(self):
        return self._hazard_features

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
        return QgsVectorLayer(self.hazard_path, '', 'ogr')

    def is_valid(self):
        """Validate InaSAFE Layer generation."""
        if self.hazard_exists and self.hazard_layer.isValid():
            return True
        return False

    def calculate_hazard_features(self):
        """Calculate important hazard features."""
        self._hazard_features = 0
        hazard_layer = self.hazard_layer
        keyword_io = KeywordIO()
        inasafe_fields = keyword_io.read_keywords(
            hazard_layer, 'inasafe_fields')
        hazard_value_field = inasafe_fields['hazard_value_field']
        for f in self.hazard_layer.getFeatures():
            try:
                hazard_val = int(f[hazard_value_field])
                if hazard_val >= 2:
                    self._hazard_features += 1
            except ValueError:
                continue
