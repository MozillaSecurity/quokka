# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import time
import threading
try:
    from queue import Queue, Empty
except ImportError as e:
    # Python 2
    from Queue import Queue, Empty


class MonitorException(Exception):
    """
    Unrecoverable error in attached monitor.
    """
    pass


class ListenerException(Exception):
    """
    Unrecoverable error in attached listener.
    """
    pass


class Listener(object):
    """
    An abstract class for providing base methods and properties to listeners.
    """

    @classmethod
    def name(cls):
        return getattr(cls, 'LISTENER_NAME', cls.__name__)

    def process_line(self, line):
        pass

    def detected_fault(self):
        return False

    def get_data(self, bucket):
        pass


class Monitor(threading.Thread):
    """
    An abstract class for providing base methods and properties to monitors.
    """

    def __init__(self, verbose=True):
        super(Monitor, self).__init__()
        self.verbose = verbose
        self.listeners = []
        self.line_queue = Queue()

    @classmethod
    def name(cls):
        return getattr(cls, 'MONITOR_NAME', cls.__name__)

    def run(self):
        line_consumer = threading.Thread(target=self.enqueue_lines)
        line_consumer.daemon = True
        line_consumer.start()

        while True:
            try:
                line = self.line_queue.get_nowait()
            except Empty:
                time.sleep(0.01)
                continue

            line = line.strip()

            if self.verbose:
                print(line)

            for listener in self.listeners:
                listener.process_line(line)

    def enqueue_lines(self):
        pass

    def stop(self):
        pass

    def add_listener(self, listener):
        assert isinstance(listener, Listener)
        self.listeners.append(listener)

    def detected_fault(self):
        return any(listener.detected_fault() for listener in self.listeners)

    def get_data(self):
        bucket = {}
        for listener in self.listeners:
            listener.get_data(bucket)
        return bucket
