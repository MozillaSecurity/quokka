# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os

from ..monitor import Listener


class ASanListener(Listener):
    LISTENER_NAME = 'AsanListener'

    def __init__(self, *args):
        super(ASanListener, self).__init__(*args)
        self.crashlog = []
        self.failure = False

    def process_line(self, line):
        if line.find('ERROR: AddressSanitizer') != -1:
            self.failure = True
        if self.failure:
            self.crashlog.append(line)

    def detected_fault(self):
        return self.failure

    def get_data(self, bucket):
        if self.crashlog:
            bucket['crashlog'] = {
                'data': os.linesep.join(self.crashlog),
                'name': 'crashlog.txt'
            }


class SyzyListener(Listener):

    LISTENER = 'SyzyAsanListener'

    def __init__(self, *args):
        super(SyzyListener, self).__init__(*args)
        self.crashlog = []
        self.failure = False

    def process_line(self, line):
        if line.find('SyzyASAN error:') != -1:
            self.failure = True
        if self.failure:
            self.crashlog.append(line)

    def detected_fault(self):
        return self.failure

    def get_data(self, bucket):
        if self.crashlog:
            bucket['crashlog'] = {
                'data': os.linesep.join(self.crashlog),
                'name': 'crashlog.txt'
            }
