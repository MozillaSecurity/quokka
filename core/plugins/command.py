# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os
import shlex
import logging

from ..quokka import ExternalProcess, PluginException


class ConsoleApplication(ExternalProcess):

    def __init__(self, quokka):
        super(ConsoleApplication, self).__init__()
        self.quokka = quokka

    def start(self):
        binary = self.quokka.plugin.kargs.get('binary')
        if not binary or not os.path.exists(binary):
            raise PluginException('%s not found.' % binary)

        params = self.quokka.plugin.kargs.get('params', '')
        cmd = [binary] + shlex.split(params)

        self.process = self.open(cmd, self.set_environ(self.quokka.get('environ')))

    def stop(self):
        if not self.process:
            return
        try:
            self.process.terminate()
            self.process.kill()
        except Exception as msg:
            logging.error(msg)
