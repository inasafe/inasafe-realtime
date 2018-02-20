# coding=utf-8
import cgi
import json
import logging
import os
import signal
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import requests

from realtime.utilities import realtime_logger_name

LOGGER = logging.getLogger(realtime_logger_name())


class InaSAFEDjangoMockServerHandler(BaseHTTPRequestHandler):

    def get_request_body(self):
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        return post_body

    def parse_request_body(self):
        ctype, pdict = cgi.parse_header(
            self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = urlparse.parse_qs(
                self.rfile.read(length), keep_blank_values=1)

            # Additional cleanup
            # by spec it will always return a list. We might don't want that.
            for key, value in postvars.iteritems():
                postvars[key] = value[0]
        elif ctype == 'application/json':
            post_body = self.get_request_body()
            postvars = json.loads(post_body)
        else:
            LOGGER.info('CTYPE: {0}'.format(ctype))
            postvars = {}
        return postvars

    def logger_GET(self):
        LOGGER.info('Mock GET Requests.')
        LOGGER.info('Request path: {0}'.format(self.path))

    def logger_POST(self):
        LOGGER.info('Mock POST Requests.')
        LOGGER.info('Request path: {0}'.format(self.path))

    def logger_PUT(self):
        LOGGER.info('Mock PUT Requests.')
        LOGGER.info('Request path: {0}'.format(self.path))

    def logger_DELETE(self):
        LOGGER.info('Mock DELETE Requests.')
        LOGGER.info('Request path: {0}'.format(self.path))

    def do_GET(self):
        self.logger_GET()
        self.send_response(requests.codes.ok)
        self.end_headers()
        return

    def do_POST(self):
        self.logger_POST()
        self.send_response(requests.codes.ok)
        LOGGER.info('Request body extraction.')
        post_body = self.get_request_body()
        LOGGER.info('Request body: {0}'.format(
            self.truncate_request_body(post_body)))
        self.end_headers()
        return

    def do_PUT(self):
        self.logger_PUT()
        self.send_response(requests.codes.ok)
        LOGGER.info('Request body extraction.')
        put_body = self.get_request_body()
        LOGGER.info('Request body: {0}'.format(
            self.truncate_request_body(put_body)))
        self.end_headers()
        return

    def do_DELETE(self):
        self.logger_DELETE()
        self.send_response(requests.codes.ok)
        self.end_headers()
        return

    @classmethod
    def truncate_request_body(cls, request_body, max_length=75):
        return (request_body[:(max_length - 4)] + ' ...') \
            if len(request_body) >= max_length else request_body


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
            except (ValueError, OverflowError):
                pass

        self.thread.start()

        with open(self.pid_file, 'w') as f:
            f.write(str(self.thread.ident))

    def shutdown(self):
        self.server.shutdown()
        self.server.server_close()
        os.remove(self.pid_file)
