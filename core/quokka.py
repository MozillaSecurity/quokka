# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import logging

from .plugin import PluginException


class QuokkaException(Exception):
    """
    Unrecoverable error in Quokka.
    """
    pass


class Quokka(object):
    """
    Quokka observer class.
    """

    def __init__(self, conf):
        self.conf = conf
        self.monitors = []
        self.loggers = []
        self.plugin = None

    @staticmethod
    def import_plugin_class(module_path):
        """Import a plugin class.

        :param module_path: Path to Python class
        :return: Class object
        """
        module_path, class_name = module_path.rsplit(".", 1)
        logging.debug("Importing '%s' from '%s'" % (class_name, module_path))
        try:
            module = __import__(module_path, fromlist=[""])
        except ImportError as msg:
            raise PluginException(msg)
        try:
            return getattr(module, class_name)
        except AttributeError as msg:
            raise PluginException(msg)

    def run_plugin(self):
        """Run a program which needs complex setup steps.

        :return: Exit code of the target process.
        """
        try:
            plugin_class = self.import_plugin_class('core.plugins.' + self.conf.plugin_class)
        except PluginException as msg:
            raise QuokkaException("Plugin initialization failed: %s" % msg)

        self.plugin = plugin_class(self.conf.quokka)
        try:
            self.plugin.start()
        except PluginException as msg:
            raise QuokkaException(msg)

        self.attach_monitors(self.plugin, self.conf.monitors)
        self.attach_loggers(self.conf.loggers)

        self.plugin.process.wait()

        self.detect_faults()

        return self.plugin.process.returncode

    def stop_plugin(self):
        """Initiate a plugin's shutdown routines by calling its stop function.

        :return: None
        """
        if not self.plugin:
            logging.info("Plugin did not start.")
            return
        if not self.plugin.is_running():
            logging.info("Plugin process exited prior with exit code: %d" % self.plugin.process.returncode)
            return
        try:
            self.plugin.stop()
        except PluginException as msg:
            raise QuokkaException(msg)

    def attach_monitors(self, plugin, monitors):
        """Attach a list of monitors and listeners to observe the target process for faults.

        :param plugin: Plugin instance
        :param monitors: List of monitors
        :return: None
        """
        for monitor in monitors:
            monitor_class = monitor.get("class")
            monitor_kargs = monitor.get("kargs")
            monitor_listeners = monitor.get("listeners")
            logging.info("Attaching monitor '%s'" % monitor_class)
            monitor_class = self.import_plugin_class('core.monitors.' + monitor_class)
            if monitor_class.MONITOR_NAME == "ConsoleMonitor":
                monitor_instance = monitor_class(plugin.process, *monitor_kargs)
            elif monitor_class.MONITOR_NAME == "WebSocketMonitor":
                pass
            else:
                logging.warning("Unsupported monitor: %s" % monitor_class)
                continue
            for listener in monitor_listeners:
                listener_class = listener.get("class")
                listener_kargs = listener.get("kargs")
                logging.info("Attaching listener '%s'" % listener_class)
                listener_class = self.import_plugin_class('core.listeners.' + listener_class)
                listener_instance = listener_class(*listener_kargs)
                monitor_instance.add_listener(listener_instance)
            monitor_instance.daemon = True
            monitor_instance.start()
            self.monitors.append(monitor_instance)

    def attach_loggers(self, loggers):
        """Attach a list of loggers to bucket the monitors found faults.

        :param loggers: A list of loggers
        :return: None
        """
        for logger in loggers:
            logger_class = logger.get("class")
            logger_kargs = logger.get("kargs")
            logging.info("Attaching logger '%s'" % logger_class)
            logger_class = self.import_plugin_class('core.loggers.' + logger_class)
            logger = logger_class(**logger_kargs)
            self.loggers.append(logger)

    def detect_faults(self):
        """Observe each attached monitor for faults and add each fault to the attached loggers.

        :return: None
        """
        for monitor in self.monitors:
            if monitor.detected_fault():
                monitor_data = monitor.get_data()
                for logger in self.loggers:
                    logger.add_to_bucket(monitor_data)
        for logger in self.loggers:
            logger.add_fault()
