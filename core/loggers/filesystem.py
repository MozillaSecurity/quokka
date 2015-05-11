# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os
import time
import logging

from ..logger import Logger


class FileLogger(Logger):
    """
    Bucket class to save crash information to disk.
    """

    BUCKET_ID = 'quokka_{}'.format(time.strftime('%a_%b_%d_%H-%M-%S_%Y'))

    def __init__(self, **kwargs):
        super(FileLogger, self).__init__()
        self.__dict__.update(kwargs)
        self.bucketpath = os.path.join(self.path, self.BUCKET_ID)
        self.faultspath = os.path.join(self.bucketpath, 'faults')
        if not self.bucketpath:
            try:
                os.makedirs(self.bucketpath)
            except OSError as e:
                logging.exception(e)

    def add_fault(self):
        faultpath = os.path.join(self.faultspath, str(self.faults))
        try:
            os.makedirs(faultpath)
        except OSError as e:
            logging.exception(e)
            return
        for name, meta in self.bucket.items():
            if 'data' not in meta or not meta['data']:
                logging.error('Bucket "{}" does not contain "data" field or field is empty.'.format(name))
                continue
            if 'name' not in meta or not meta['name']:
                logging.error('Bucket "{}" does not contain "name" field or field is empty.'.format(name))
                continue
            filename = os.path.join(faultpath, meta['name'])
            try:
                with open(filename, 'wb') as fo:
                    fo.write(meta['data'].encode('UTF-8'))
            except IOError as e:
                logging.exception(e)

    @property
    def faults(self):
        count = 0
        if not os.path.exists(self.faultspath):
            return count
        for item in os.listdir(self.faultspath):
            item = os.path.join(self.faultspath, item)
            if os.path.isdir(item) and not item.startswith('.'):
                count += 1
        return count
