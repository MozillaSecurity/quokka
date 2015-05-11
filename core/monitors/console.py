# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from ..monitor import Monitor


class ConsoleMonitor(Monitor):
    MONITOR_NAME = 'ConsoleMonitor'

    def __init__(self, process, *args, **kwargs):
        super(ConsoleMonitor, self).__init__(*args, **kwargs)
        self.out = process.stdout

    def enqueue_lines(self):
        for line in iter(self.out.readline, ''):
            self.line_queue.put(line)
        self.out.close()

