# coding=utf-8
from realtime.exceptions import FloodDataSourceAPIError

from realtime.flood.data_source.dummy_source_api import DummySourceAPI
from realtime.flood.data_source.flood_data_source import PetaJakartaAPI, \
    PetaBencanaAPI, PetaBencanaDevAPI

DATA_SOURCE_LIST = [
    DummySourceAPI,
    PetaJakartaAPI,
    PetaBencanaAPI,
    PetaBencanaDevAPI
]

DATA_SOURCE_DICT = {
    data_source.source_key(): data_source
    for data_source in DATA_SOURCE_LIST
}


def load_data_api_object(data_source):
    """Load API to get Flood data

    :param data_source: the name of the data source
    :type data_source: str

    :return: Data API
    :rtype:
        realtime.flood.data_source.flood_data_source.FloodHazardBaseClassAPI
    """
    if data_source in DATA_SOURCE_DICT:
        return DATA_SOURCE_DICT[data_source]()
    raise FloodDataSourceAPIError(
        'This data source is not supported or wrong name provided.')
