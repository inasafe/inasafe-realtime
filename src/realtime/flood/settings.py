# coding=utf-8


FLOOD_ID_FORMAT = '{event_time:%Y%m%d%H}-{duration}-{level}'
FLOOD_ID_REGEXP = r'^(?P<year>\d{4})' \
                  r'(?P<month>\d{2})' \
                  r'(?P<day>\d{2})' \
                  r'(?P<hour>\d{2})-' \
                  r'(?P<duration>\d{1})-' \
                  r'(?P<level>\w+)$'

FLOOD_HAZARD_DEFAULT_BASENAME = 'flood_data'
