# coding=utf-8


FLOOD_ID_FORMAT = '{time:%Y%m%d%H}-{duration}-{level}'
FLOOD_ID_REGEXP = r'^(?P<year>\d{4})' \
                  r'(?P<month>\d{2})' \
                  r'(?P<day>\d{2})' \
                  r'(?P<hour>\d{2})-' \
                  r'(?P<_duration>\d{1})-' \
                  r'(?P<_level>\w+)$'

FLOOD_HAZARD_DEFAULT_BASENAME = 'flood_data'
