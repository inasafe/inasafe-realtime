# coding=utf-8


ASH_ID_FORMAT = '{event_time:%Y%m%d%H%M%z}_{volcano_name}'

ASH_ID_REGEXP = r'^(?P<year>\d{4})' \
                r'(?P<month>\d{2})' \
                r'(?P<day>\d{2})' \
                r'(?P<hour>\d{2})' \
                r'(?P<minute>\d{2})' \
                r'(?P<timezone_offset>[\+-]\d{4})_' \
                r'(?P<volcano_name>[\w-]+)'

ASH_HAZARD_DEFAULT_BASENAME = 'ash_fall'

ASH_DATETIME_FORMAT = '{event_time:%Y-%m-%d %H:%M:%S %z}'

ASH_TIMESTAMP_FORMAT = '{event_time:%Y%m%d%H%M%S%z}'
