# coding=utf-8
from realtime.flood.data_source.flood_data_source import \
    FloodHazardBaseClassAPI

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/19/16'


class DummySourceAPI(FloodHazardBaseClassAPI):

    @classmethod
    def get_aggregate_report(cls, filename):
        return open(filename).read()

    @classmethod
    def source_name(cls):
        return 'Hazard File'

    @classmethod
    def source_key(cls):
        return 'hazard_file'

    @classmethod
    def region_name(cls):
        return 'Jakarta'
