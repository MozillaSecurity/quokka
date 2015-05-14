# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os
import shlex
import shutil
import logging
import tempfile

from ..quokka import ExternalProcess, PluginException


class FirefoxApplication(ExternalProcess):

    def __init__(self, quokka):
        super(FirefoxApplication, self).__init__()
        self.quokka = quokka

        self.profile_path = ''

    def start(self):
        binary = self.quokka.plugin.kargs.get('binary')
        if not binary or not os.path.exists(binary):
            raise PluginException('%s not found.' % binary)

        params = self.quokka.plugin.kargs.get('params', '')

        environ = self.set_environ(self.quokka.get('environ'))

        prefs = self.quokka.plugin.kargs.get('prefs')
        if not prefs or not os.path.exists(prefs):
            raise PluginException('No preferences provided.')

        self.profile_path = tempfile.mkdtemp()
        profile_name = os.path.basename(self.profile_path)
        cmd = [binary, '-no-remote', '-CreateProfile', '%s %s' % (profile_name, self.profile_path)]
        self.call(cmd, environ)

        shutil.copyfile(prefs, os.path.join(self.profile_path, 'prefs.js'))
        print(prefs)
        cmd = [binary, '-P', profile_name] + shlex.split(params)

        self.process = self.open(cmd, environ)

    def stop(self):
        if os.path.isdir(self.profile_path):
            logging.info("Deleting Firefox profile path: %s" % self.profile_path)
            try:
                shutil.rmtree(self.profile_path)
            except Exception as msg:
                logging.error(msg)
        if self.process:
            try:
                self.process.terminate()
                self.process.kill()
            except Exception as msg:
                logging.error(msg)
