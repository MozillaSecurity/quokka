# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import logging
try:
    from socketserver import TCPServer
except ImportError:
    from SocketServer import TCPServer

from .. import websocket
from ..monitor import Monitor


class WebSocketMonitor(Monitor):
    MONITOR_NAME = 'WebSocketMonitor'

    def __init__(self, addr_port=('', 9999), *args, **kwargs):
        super(WebSocketMonitor, self).__init__(*args, **kwargs)
        self.addr_port = addr_port
        self.server = None

    def enqueue_lines(self):
        run = True
        line_queue = self.line_queue

        class WebSocketHandler(websocket.BaseWebSocketHandler):
            def on_message(self, message):
                line_queue.put(message)

            def should_close(self):
                return not run

        class _TCPServer(TCPServer):
            allow_reuse_address = True

        self.server = _TCPServer(self.addr_port, WebSocketHandler)
        try:
            self.server.serve_forever()
        finally:
            run = False

    def stop(self):
        if self.server:
            try:
                self.server.shutdown()
            except Exception as e:
                logging.exception(e)
