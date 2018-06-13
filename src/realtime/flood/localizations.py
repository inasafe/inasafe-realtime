# coding=utf-8
from PyQt4.QtCore import QObject


class FloodHazardString(QObject):

    def __init__(self):
        super(FloodHazardString, self).__init__()

    @property
    def hazard_title(self):
        return self.tr('Jakarta Floods - {timestamp}')
