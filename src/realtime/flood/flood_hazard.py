# coding=utf-8
import logging
import os
from shutil import copy

from PyQt4.QtCore import QObject
from qgis.core import QgsVectorLayer

from realtime.flood.localizations import FloodHazardString
from realtime.flood.settings import FLOOD_HAZARD_DEFAULT_BASENAME
from realtime.utilities import realtime_logger_name
from safe.utilities.keyword_io import KeywordIO

LOGGER = logging.getLogger(realtime_logger_name())


class FloodHazard(QObject):
    """Class placeholder for Flood hazard object."""

    def __init__(
            self, flood_id, event_time, time_zone, duration, level,
            geojson_file_path,
            data_source, output_dir=None, output_basename=None):
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
        self._flood_id = flood_id
        self._event_time = event_time
        self._time_zone = time_zone
        self._duration = duration
        self._level = level
        self._data_source = data_source

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
        """Copy style from the OSM resource directory to the output path.

        .. versionadded: 3.3

        """
        source_qml_path = self.resource_path('flood-style.qml')
        output_qml_path = self.hazard_path.replace('json', 'qml')
        LOGGER.info('Copying qml to: {0}'.format(output_qml_path))
        copy(source_qml_path, output_qml_path)

    def write_keywords(self):
        keyword_io = KeywordIO()

        keywords = {
            'hazard_category': u'single_event',
            'title': self.localization.hazard_title.format(
                timestamp=self.event_time_in_time_zone),
            'keyword_version': u'4.3',
            'value_maps': {
                u'structure': {
                    u'flood_hazard_classes': {
                        u'active': False,
                        u'classes': {u'dry': [0, 1], u'wet': [2, 3, 4]}
                    }, u'flood_petabencana_hazard_classes': {
                        u'active': True, u'classes': {
                            u'high': [4], u'medium': [3], u'use_caution': [1],
                            u'low': [2]
                        }
                    }
                }, u'place': {
                    u'flood_hazard_classes': {
                        u'active': False,
                        u'classes': {u'dry': [0, 1], u'wet': [3, 4, 2]}
                    }, u'flood_petabencana_hazard_classes': {
                        u'active': True, u'classes': {
                            u'high': [4], u'medium': [3], u'use_caution': [1],
                            u'low': [2]
                        }
                    }
                }, u'land_cover': {
                    u'flood_hazard_classes': {
                        u'active': False,
                        u'classes': {u'dry': [0, 1], u'wet': [2, 3, 4]}
                    }, u'flood_petabencana_hazard_classes': {
                        u'active': True, u'classes': {
                            u'high': [4], u'medium': [3], u'use_caution': [1],
                            u'low': [2]
                        }
                    }
                }, u'road': {
                    u'flood_hazard_classes': {
                        u'active': False,
                        u'classes': {u'dry': [0, 1], u'wet': [3, 2, 4]}
                    }, u'flood_petabencana_hazard_classes': {
                        u'active': True, u'classes': {
                            u'high': [4], u'medium': [3], u'use_caution': [1],
                            u'low': [2]
                        }
                    }
                }, u'population': {
                    u'flood_hazard_classes': {
                        u'active': False,
                        u'classes': {u'dry': [0, 1], u'wet': [2, 3, 4]}
                    }, u'flood_petabencana_hazard_classes': {
                        u'active': True, u'classes': {
                            u'high': [4], u'medium': [3], u'use_caution': [1],
                            u'low': [2]
                        }
                    }
                }
            },
            'hazard': u'flood',
            'source': self.data_source.source_name(),
            'layer_purpose': u'hazard',
            'layer_geometry': u'polygon',
            'inasafe_fields': {u'hazard_value_field': u'state'},
            'layer_mode': u'classified'
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
            except BaseException:
                continue
