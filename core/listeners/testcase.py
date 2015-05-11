# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os
import json

from ..monitor import Listener


class TestcaseListener(Listener):
    LISTENER_NAME = 'TestcaseListener'

    def __init__(self, *args):
        super(TestcaseListener, self).__init__(*args)
        self.testcase = []

    def process_line(self, line):
        if line.find('NEXT TESTCASE') != -1:
            self.testcase = []
        if line.startswith('/*L*/'):
        #if line.find("/*L*/") != -1: # For Chromium
            self.testcase.append(json.loads(line[5:]))

    def detected_fault(self):
        return True

    def get_data(self, bucket):
        if self.testcase:
            bucket['testcase'] = {
                'data': os.linesep.join(self.testcase),
                'name': 'testcase.txt'
            }
