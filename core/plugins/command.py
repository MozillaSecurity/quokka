# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os

from ..quokka import ExternalProcess, PluginException


class ConsoleApplication(ExternalProcess):

    def __init__(self, conf):
        super(ConsoleApplication, self).__init__()
        self.quokka = conf.quokka
        self.plugin = conf.plugin_kargs

    def start(self):
        binary = self.plugin['binary']
        if not binary or not os.path.exists(binary):
            raise PluginException('%s not found.' % binary)

        params = self.plugin['params']
        environ = self.set_environ(self.quokka['environ'])

        cmd = [binary]
        if params:
            cmd.append(params)

        self.process = self.open(cmd, environ)
