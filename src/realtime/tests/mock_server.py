# coding=utf-8
import logging
import requests

from http.server import BaseHTTPRequestHandler
from realtime.utilities import realtime_logger_name

LOGGER = logging.getLogger(realtime_logger_name())


class InaSAFEDjangoMockServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        LOGGER.info('Mock GET Requests.')
        LOGGER.info('Request path: {0}'.format(self.path))
        self.send_response(requests.codes.ok)
        self.end_headers()
        return

    def do_POST(self):
        LOGGER.info('Mock POST Requests.')
        LOGGER.info('Request path: {0}'.format(self.path))
        self.send_response(requests.codes.ok)
        self.end_headers()
        return

    def do_PUT(self):
        LOGGER.info('Mock PUT Requests.')
        LOGGER.info('Request path: {0}'.format(self.path))
        self.send_response(requests.codes.ok)
        self.end_headers()
        return

    def do_DELETE(self):
        LOGGER.info('Mock DELETE Requests.')
        LOGGER.info('Request path: {0}'.format(self.path))
        self.send_response(requests.codes.ok)
        self.end_headers()
        return
