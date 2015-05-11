# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import re
import json
import types
import logging

from .quokka import QuokkaException


class AttributeTree(dict):

    def __init__(self, value=None):
        if value is None:
            pass
        elif isinstance(value, dict):
            for key in value:
                self.__setitem__(key, value[key])
        else:
            raise TypeError('Expected dict()')

    def __setitem__(self, key, value):
        if '.' in key:
            my_key, rest_of_key = key.split('.', 1)
            target = self.setdefault(my_key, AttributeTree())
            if not isinstance(target, AttributeTree):
                raise KeyError('Can not set "%s" in "%s" (%s)' % (rest_of_key, my_key, repr(target)))
            target[rest_of_key] = value
        else:
            if isinstance(value, dict) and not isinstance(value, AttributeTree):
                value = AttributeTree(value)
            dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        if '.' not in key:
            return dict.__getitem__(self, key)
        my_key, rest_of_key = key.split('.', 1)
        target = dict.__getitem__(self, my_key)
        if not isinstance(target, AttributeTree):
            raise KeyError('Can not get "%s" in "%s" (%s)' % (rest_of_key, my_key, repr(target)))
        return target[rest_of_key]

    def __contains__(self, key):
        if '.' not in key:
            return dict.__contains__(self, key)
        my_key, rest_of_key = key.split('.', 1)
        target = dict.__getitem__(self, my_key)
        if not isinstance(target, AttributeTree):
            return False
        return rest_of_key in target

    def setdefault(self, key, default):
        if key not in self:
            self[key] = default
        return self[key]

    __setattr__ = __setitem__
    __getattr__ = __getitem__


class QuokkaConf(object):

    def __init__(self, conf):
        try:
            conf = json.loads(conf)
        except ValueError as msg:
            raise QuokkaException('Unable to parse Quokka configuration: %s' % msg)
        self.quokka = AttributeTree(conf)
        self.plugin = {}

    def add_plugin_conf(self, conf):
        try:
            conf = json.loads(conf)
        except ValueError as msg:
            raise QuokkaException('Unable to parse plugin configuration: %s' % msg)
        self.plugin = AttributeTree(conf)
        logging.info('Merging plugin configuration with Quokka.')
        self.quokka = self.merge(self.quokka, self.plugin)

    @staticmethod
    def merge(x, y):
        # Store a copy of x, but overwrite with y's values where applicable.
        merged = dict(x, **y)
        xkeys = x.keys()
        # If the value of merged[key] was overwritten with y[key]'s value, we put back any missing x[key] values.
        for key in xkeys:
            # If this key is a dictionary, recurse
            if isinstance(x[key], dict) and key in y:
                merged[key] = QuokkaConf.merge(x[key], y[key])
        return merged

    @staticmethod
    def set_conf_vars(conf, vars):
        conf_vars = re.findall("@(.*?)@", conf)
        for var in conf_vars:
            if var not in vars:
                logging.error('Undefined variable @%s@ in configuration', var)
                return
            conf = conf.replace('@%s@' % var, vars[var])
        return conf

    @staticmethod
    def list_conf_vars(conf):
        return re.findall("@(.*?)@", conf)

    @property
    def plugin_path(self):
        plugin_path = self.plugin.get("plugin")
        if not plugin_path:
            raise QuokkaException("Missing plugin path.")
        return plugin_path
