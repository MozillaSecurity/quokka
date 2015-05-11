# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


class Logger(object):
    """
    Parent class for collecting buckets.
    """

    def __init__(self):
        self.bucket = {}

    def add_to_bucket(self, data):
        self.bucket.update(data)

    def add_fault(self):
        pass
