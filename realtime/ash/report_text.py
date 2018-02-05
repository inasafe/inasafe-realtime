# coding=utf-8

from PyQt4.QtCore import QObject

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/11/2017'


class ReportText(QObject):
    """Placeholder class for texts in the report."""

    def __init__(self):
        QObject.__init__(self)

    def qpt_token(
            self,
            volcano_name=None, time=None, region=None,
            alert_level=None, longitude_string=None, latitude_string=None,
            eruption_height=0, vent_height=0,
            forecast_duration=None,elapsed_hour=None,
            elapsed_minute=None, version=None):
        """Token string for QPT template"""

        eruption_height_asl = eruption_height + vent_height

        event = {
            # This section is from event variable
            'event-volcano-name': volcano_name,
            'event-time': self.tr('{time:%-d-%b-%Y %H:%M:%S}').format(
                time=time),
            'event-region': str(region),
            'event-alert-level': alert_level,
            'event-longitude': longitude_string,
            'event-latitude': latitude_string,
            'event-eruption-height': str(eruption_height),
            'event-vent-height': str(vent_height),
            'event-forecast-duration': str(forecast_duration),
            'event-eruption-height-asl': str(eruption_height_asl),
            'event-elapsed-hour': str(elapsed_hour),
            'event-elapsed-minute': str(elapsed_minute),
            'inasafe-version': version,

            # This section is from pregenerated variable
            'report-title': self.tr('Volcanic Ash Impact'),
            'report-timestamp': self.tr(
                'Volcano: {volcano_name}, {time:%-d-%b-%Y %H:%M:%S} '
                '{zone} {time:%z}').format(
                    volcano_name=volcano_name,
                    time=time,
                    zone=time.tzinfo.zone),
            'report-province': self.tr('Province: {region}').format(
                region=region),
            'report-alert-level': self.tr(
                'Alert Level: {alert_level}').format(
                    alert_level=alert_level.capitalize()),
            'report-location': self.tr(
                'Position: {lon}, {lat}; '
                'Eruption Column Height (a.s.l) '
                '- {eruption_height_asl} m').format(
                    lon=longitude_string,
                    lat=latitude_string,
                    eruption_height_asl=eruption_height_asl),
            'report-elapsed': self.tr(
                'Elapsed time since event: '
                '{hour} hour(s) and {minute} minute(s)').format(
                    hour=elapsed_hour, minute=elapsed_minute),
            'header-impact-table': self.tr(
                'Potential impact at each fallout level'),
            'header-nearby-table': self.tr('Nearby places'),
            'header-landcover-table': self.tr('Land Cover Impact'),
            'content-disclaimer': self.tr(
                'The impact estimation is automatically generated and only '
                'takes into account the population, cities and land cover '
                'affected by different levels of volcanic ash fallout on the '
                'ground. The estimate is based on volcanic ash fallout data '
                'from Badan Geologi, population count data derived by '
                'DMInnovation from worldpop.org.uk, place information and '
                'land cover classification data provided by Indonesian '
                'Geospatial Portal at http://portal.ina-sdi.or.id and '
                'software developed by BNPB. Limitation in the estimates of '
                'surface fallout, population and place names datasets may '
                'result in a significant misrepresentation of the on-the-'
                'surface situation in the figures shown here. Consequently, '
                'decisions should not be made solely on the information '
                'presented here and should always be verified by ground '
                'truthing and other reliable information sources.'
            ),
            'content-notes': self.tr(
                'This report was created using InaSAFE version {version}. '
                'Visit http://inasafe.org for more information. ').format(
                    version=version),
            'content-airport-notes': self.tr(
                'This report does not include the potential impact of '
                'airborne volcanic ash on aviation services. Nearby airports '
                'may already be affected or become affected in future by ash '
                'fall on ground or other hazards.'
            ),
            'content-support': self.tr(
                'Supported by DMInnovation, Geoscience Australia and '
                'the World Bank-GFDRR')
        }
        return event

    def population_table_token(self):
        table_header = [
            {
                'header': self.tr('Fallout Level')
            },
            {
                'header': self.tr('Very Low'),
                'class': 'lv1'
            },
            {
                'header': self.tr('Low'),
                'class': 'lv2'
            },
            {
                'header': self.tr('Moderate'),
                'class': 'lv3'
            },
            {
                'header': self.tr('High'),
                'class': 'lv4'
            },
            {
                'header': self.tr('Very High'),
                'class': 'lv5'
            },
        ]

        potential_impact_header = [
            self.tr('Potential Impact'),
            self.tr(
                'Impact on health (respiration), livestock, and contamination '
                'of water supply.'),
            self.tr(
                'Damage to transportation routes (e.g. airports, roads, '
                'railways); damage to critical infrastructure (e.g. '
                'electricity supply); damage to more vulnerable agricultural '
                'crops (e.g. rice fields)'),
            self.tr(
                'Damage to less vulnerable agricultural crops (e.g. tea '
                'plantations) and destruction of more vulnerable crops; '
                'destruction of critical infrastructure; cosmetic '
                '(non-structural) damage to buildings'),
            self.tr(
                'Dry loading on buildings causing structural damage but not '
                'collapse; Wet loading on buildings (i.e. ash loading + heavy '
                'rainfall) causing structural collapse.'),
            self.tr('Dry loading on buildings causing structural collapse.')
        ]

        context = {
            'table_header': table_header,
            'affected_header': self.tr('Estimated People Affected'),
            'potential_impact_header': potential_impact_header,
            'ash_thickness_header': self.tr('Ash Thickness Range (cm)')
        }
        return context

    def landcover_table_token(self, landcover_list=None):
        # Landcover type localization for dynamic translations:
        # noqa
        landcover_types = [
            self.tr('Forest'),
            self.tr('Plantation'),
            self.tr('Water Supply'),
            self.tr('Settlement'),
            self.tr('Rice Field')
        ]

        context = {
            'landcover_list': landcover_list,
            'landcover_type_header': self.tr('Land Cover Type'),
            'landcover_area_header': self.tr('Area affected (km<sup>2</sup>)'),
            'empty_rows': self.tr('No area affected')
        }

        return context

    def hazard_label_token(self):
        return {
            0: self.tr('Very Low'),
            1: self.tr('Low'),
            2: self.tr('Moderate'),
            3: self.tr('High'),
            4: self.tr('Very High')
        }

    def nearby_table_token(self, item_list=None):
        return {
            'item_list': item_list,
            'name_header': self.tr('Name'),
            'affected_header': self.tr('People / Airport affected'),
            'fallout_header': self.tr('Fallout Level'),
            'empty_rows': self.tr('No nearby cities or airports are affected '
                                  'by forecast ash fall on the ground in this '
                                  'report')
        }
