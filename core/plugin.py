# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os
import sys
import time
import logging
import subprocess


class PluginException(Exception):
    """
    Unrecoverable error in external process.
    """
    pass


class BasePlugin(object):
    """
    An abstract class for providing base methods and properties to plugins.
    """

    def __init__(self, quokka):
        self.quokka = quokka

    @classmethod
    def name(cls):
        return getattr(cls, 'PLUGIN_NAME', cls.__name__)

    @classmethod
    def version(cls):
        return getattr(cls, 'PLUGIN_VERSION', '0.1')

    def start(self):
        pass

    def stop(self):
        pass



class PluginProcess(BasePlugin):
    """
    Parent class for plugins which make use of external tools.
    """

    def __init__(self):
        self.process = None

    def open(self, cmd, env=None, cwd=None):
        logging.info('Running command: {}'.format(cmd))
        self.process = subprocess.Popen(cmd,
                                        universal_newlines=True,
                                        env=env or os.environ,
                                        cwd=cwd,
                                        stderr=subprocess.STDOUT,
                                        stdout=subprocess.PIPE,
                                        bufsize=1,
                                        close_fds='posix' in sys.builtin_module_names)
        return self.process

    @staticmethod
    def call(cmd, env=None, cwd=None):
        logging.info('Calling command: {}'.format(cmd))
        return subprocess.check_call(cmd, env=env, cwd=cwd)

    def wait(self, timeout=600):
        if timeout:
            end_time = time.time() + timeout
            interval = min(timeout / 1000.0, .25)
            while True:
                result = self.process.poll()
                if result is not None:
                    return result
                if time.time() >= end_time:
                    break
                time.sleep(interval)
            self.stop()
        self.process.wait()

    @staticmethod
    def set_environ(context=None):
        env = os.environ
        if context is None:
            return env
        for key, val in context.items():
            if isinstance(val, dict):
                env[key] = ','.join('{!s}={!r}'.format(k, v) for (k, v) in val.items())
            else:
                env[key] = val
        return env

    def is_running(self):
        if self.process is None:
            return False
        if self.process.poll() is not None:
            return False
        return True

    def stop(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.kill()
            except Exception as e:
                logging.error(e)
