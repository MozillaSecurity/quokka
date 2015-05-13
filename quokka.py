#!/usr/bin/env python
# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Quokka is a utility to run and monitor a to fuzzed application.
"""
import os
import sys
import logging
import argparse

from core.quokka import Quokka, Utilities, QuokkaException
from core.config import QuokkaConf


class QuokkaCommandLine(object):
    """
    Command-line interface for Quokka
    """
    HOME = os.path.dirname(os.path.abspath(__file__))
    VERSION = 0.1
    CONFIG_PATH = os.path.relpath(os.path.join(HOME, 'configs'))
    QUOKKA_CONFIG = os.path.join(CONFIG_PATH, 'quokka.json')

    def parse_args(self):
        parser = argparse.ArgumentParser(description='Quokka Runtime',
                                         prog=__file__,
                                         add_help=False,
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                         epilog='The exit status is 0 for non-failures and 1 for failures.')

        m = parser.add_argument_group('Mandatory Arguments')
        g = m.add_mutually_exclusive_group(required=True)
        g.add_argument('-command', metavar='str', type=str, help='Run an application.')
        g.add_argument('-plugin', metavar='file', type=argparse.FileType(),
                       help='Run an application with a setup script.')

        o = parser.add_argument_group('Optional Arguments')
        o.add_argument('-quokka', metavar='file', type=argparse.FileType(), default=self.QUOKKA_CONFIG,
                       help='Quokka configuration')
        o.add_argument('-conf-args', metavar='k=v', nargs='+', type=str, help='Add/edit configuration properties.')
        o.add_argument('-conf-vars', metavar='k=v', nargs='+', type=str, help='Subsitute configuration variables.')
        o.add_argument('-list-conf-vars', action='store_true', help='List used configuration variables.')
        o.add_argument('-verbosity', metavar='{1..5}', default=2, type=int, choices=list(range(1, 6, 1)),
                       help='Level of verbosity for logging module.')
        o.add_argument('-h', '-help', '--help', action='help', help=argparse.SUPPRESS)
        o.add_argument('-version', action='version', version='%(prog)s {}'.format(self.VERSION), help=argparse.SUPPRESS)

        return parser.parse_args()

    def main(self):
        args = self.parse_args()

        logging.basicConfig(format='[Quokka] %(asctime)s %(levelname)s: %(message)s',
                            level=args.verbosity * 10,
                            datefmt='%Y-%m-%d %H:%M:%S')

        if args.list_conf_vars:
            conf_vars = []
            try:
                conf_vars.extend(QuokkaConf.list_conf_vars(args.quokka.read()))
                if args.plugin:
                    conf_vars.extend(QuokkaConf.list_conf_vars(args.plugin.read()))
            except QuokkaException as msg:
                logging.error(msg)
                return 1
            if len(conf_vars):
                logging.info("List of available configuration variables:")
                for v in conf_vars:
                    logging.info('\t%r', v)
            return 0

        logging.info('Loading Quokka configuration from %s' % args.quokka.name)
        try:
            quokka_conf = args.quokka.read()
            if args.conf_vars:
                quokka_conf = QuokkaConf.set_conf_vars(quokka_conf, Utilities.pair_to_dict(args.conf_vars))
            quokka_conf = QuokkaConf(quokka_conf)
        except QuokkaException as msg:
            logging.error(msg)
            return 1

        if args.plugin:
            logging.info('Loading plugin configuration from %s' % args.plugin.name)
            try:
                plugin_conf = args.plugin.read()
                if args.conf_vars:
                    plugin_conf = QuokkaConf.set_conf_vars(plugin_conf, Utilities.pair_to_dict(args.conf_vars))
                quokka_conf.add_plugin_conf(plugin_conf)
            except QuokkaException as msg:
                logging.error(msg)
                return 1

        if args.conf_args:
            logging.info('Updating configuration on request.')
            conf_args = Utilities.pair_to_dict(args.conf_args)
            for k, v in conf_args.items():
                if k in quokka_conf.quokka:
                    print(k)
                    quokka_conf.quokka[k] = v

        if args.command:
            try:
                quokka = Quokka(quokka_conf)
                quokka.run_command(args.command)
            except QuokkaException as msg:
                logging.error(msg)
                return 1
            except KeyboardInterrupt:
                print('')
                logging.info("Caught SIGINT, aborting...")
                return 0

        if args.plugin:
            try:
                quokka = Quokka(quokka_conf)
                quokka.run_plugin()
            except QuokkaException as msg:
                logging.error(msg)
                return 1
            except KeyboardInterrupt:
                print('')
                logging.info("Caught SIGINT, aborting...")
                return 0

        return 0


if __name__ == '__main__':
    sys.exit(QuokkaCommandLine().main())
