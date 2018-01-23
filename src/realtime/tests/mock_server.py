# coding=utf-8
import logging
import os
import signal
from threading import Thread

import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

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


class InaSAFEDjangoMockServer(object):
    pid_file = '/var/run/.inasafe_django_mock_server.pid'

    def __init__(self, host, port, handler):
        HTTPServer.allow_reuse_address = True
        self._server = HTTPServer((host, port), handler)
        self._thread = Thread(
            target=self.server.serve_forever)
        self.thread.setDaemon(True)

    @property
    def server(self):
        return self._server

    @property
    def thread(self):
        return self._thread

    def start_server(self):
        """Start and track that the server is running."""
        # Configure Mock Server
        if os.path.exists(self.pid_file):
            with open(self.pid_file) as f:
                pid = f.read()

            try:
                pid_number = int(pid)

                # attempt to shutdown pid
                os.kill(pid_number, signal.SIGTERM)
            except ValueError:
                pass

        self.thread.start()

        with open(self.pid_file, 'w') as f:
            f.write(str(self.thread.ident))

    def shutdown(self):
        self.server.shutdown()
        self.server.server_close()
        os.remove(self.pid_file)
