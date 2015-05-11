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


class QuokkaException(Exception):
    """
    Unrecoverable error in Quokka.
    """
    pass


class BasePlugin(object):
    """
    An abstract class for providing base methods and properties to plugins.
    """

    @classmethod
    def name(cls):
        return getattr(cls, 'PLUGIN_NAME', cls.__name__)

    @classmethod
    def version(cls):
        return getattr(cls, 'PLUGIN_VERSION', '0.1')

    def open(self, *args):
        pass

    def stop(self):
        pass


class ModuleImporter(object):
    def __init__(self, module_path):
        self.class_name = module_path.split(".")[-1]
        self.module_path = ".".join(module_path.split(".")[:-1])

    def klass(self):
        logging.debug("Importing '%s' from '%s'" % (self.class_name, self.module_path))
        module = __import__(self.module_path, fromlist=[""])
        return getattr(module, self.class_name)


class ExternalProcess(BasePlugin):
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
                env[key] = ' '.join('{!s}={!r}'.format(k, v) for (k, v) in val.items())
            else:
                env[key] = val
        return env

    def stop(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.kill()
            except Exception as e:
                logging.error(e)


class Quokka(object):
    """
    Quokka.
    """

    def __init__(self, conf):
        self.conf = conf
        self.monitors = []
        self.loggers = []

    def detect_faults(self):
        """Observe each attached monitor for faults and add each fault to the attached loggers."""
        for monitor in self.monitors:
            if monitor.detected_fault():
                monitor_data = monitor.get_data()
                for logger in self.loggers:
                    logger.add_to_bucket(monitor_data)
        for logger in self.loggers:
            logger.add_fault()

    def run_command(self):
        pass

    def run_plugin(self):
        # Plugin
        try:
            plugin_class = ModuleImporter('core.plugins.' + self.conf.plugin_path).klass()
        except PluginException as msg:
            raise QuokkaException("Plugin initialization failed: %s" % msg)
        plugin_settings = self.conf.plugin.get("configuration")
        plugin = plugin_class(plugin_settings)
        try:
            plugin.start()
        except PluginException as msg:
            raise QuokkaException(msg)

        # Monitors and Listeners
        monitors = self.conf.plugin.get("monitors")
        if not monitors:
            monitors = self.conf.quokka.get("monitors")
            if not monitors:
                raise QuokkaException("No monitors to attach.")
        self.attach_monitors(plugin, monitors)

        # Loggers
        loggers = self.conf.plugin.get("loggers")
        if not loggers:
            loggers = self.conf.quokka.get("loggers")
            if not loggers:
                raise QuokkaException("No loggers to attach.")
        self.attach_loggers(loggers)

        plugin.process.wait()

        self.detect_faults()

        return plugin.process.returncode

    def attach_monitors(self, plugin, monitors):
        for monitor in monitors:
            monitor_path = monitor[0]
            logging.info("Attaching monitor '%s'" % monitor_path)
            monitor_class = ModuleImporter('core.monitors.' + monitor_path).klass()
            if monitor_class.MONITOR_NAME == "ConsoleMonitor":
                monitor_instance = monitor_class(plugin.process)
            elif monitor_class.MONITOR_NAME == "WebSocketMonitor":
                pass
            else:
                logging.warning("Dropping %s" % monitor_path)
                continue
            for listener_path in monitor[1]:
                logging.info("Attaching listener '%s'" % listener_path)
                listener_class = ModuleImporter('core.listeners.' + listener_path).klass()
                monitor_instance.add_listener(listener_class())

            monitor_instance.daemon = True
            monitor_instance.start()
            self.monitors.append(monitor_instance)

    def attach_loggers(self, loggers):
        for logger in loggers:
            logger_path, logger_settings = logger[0], logger[1]
            logging.info("Attaching logger '%s'" % logger_path)
            logger_class = ModuleImporter('core.loggers.' + logger_path).klass()
            logger = logger_class(**logger_settings)
            self.loggers.append(logger)
