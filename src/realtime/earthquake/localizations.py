# coding=utf-8
from PyQt4.QtCore import QObject


class ShakeHazardString(QObject):

    def __init__(self):
        super(ShakeHazardString, self).__init__()

    @property
    def shake_title_format(self):
        return self.tr('Shakemap {event_id}')

    @property
    def grid_source(self):
        return self.tr(
            'BMKG (Badan Meteorologi, Klimatologi, dan Geofisika) '
            'Indonesia')
