# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os

from ..quokka import ExternalProcess, PluginException


class DefaultPlugin(ExternalProcess):
    PLUGIN_NAME = 'Default'

    def start(self):
        application = self.configuration['application']
        if not application or not os.path.exists(application):
            raise PluginException('{} not found.'.format(application))
        arguments = self.configuration['arguments']
        environment = self.configuration['environment']
        cmd = [application]
        if arguments:
            cmd.extend(arguments)
        cmd.append(self.target)
        self.process = self.open(cmd, self.setup_environ(environment))
