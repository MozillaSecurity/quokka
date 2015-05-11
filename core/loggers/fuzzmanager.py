# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os
import sys
import zipfile
import logging
import StringIO
import tempfile
import platform
import subprocess
try:
    sys.path.append("utils/FuzzManager")
    from FTB.ProgramConfiguration import ProgramConfiguration
    from FTB.Signatures.CrashInfo import CrashInfo
    from Collector.Collector import Collector
except ImportError as msg:
    logging.warning("FuzzManager is missing or one of its dependencies: %s" % msg)

from ..logger import Logger

try:
    class FuzzManagerLogger(Logger):
        """FuzzManager Logger"""
        def __init__(self, **kwargs):
            super(FuzzManagerLogger, self).__init__()
            self.__dict__.update(kwargs)
            self.cache_dir = self.cache_dir or tempfile.gettempdir()
            self.server_host = self.server_host or "127.0.0.1"
            self.server_port = self.server_port or "8000"
            self.server_protocol = self.server_protocol or "http"
            self.server_auth_token = self.server_auth_token or ""
            if not self.client_id:
                try:
                    self.client_id = "_framboise"
                except subprocess.CalledProcessError:
                    self.client_id = "framboise"
            self.product = self.product or "N/A"
            self.version = self.version or "N/A"

        def add_fault(self):
            meta_command = []
            asan_report = self.bucket["crashlog"]["data"]
            # Setup FuzzManager with information about target and platform data.
            program_configuration = ProgramConfiguration(self.product,
                                                         platform.machine(),
                                                         platform.system(),
                                                         self.version,
                                                         os.environ.data,
                                                         meta_command)
            # Prepare FuzzManager with target and crash information.
            crash_info = CrashInfo.fromRawCrashData("",
                                                    "",
                                                    program_configuration,
                                                    asan_report)
            # Sign into FuzzManager.
            collector = Collector(self.cache_dir,
                                  serverHost=self.server_host,
                                  serverPort=self.server_port,
                                  serverProtocol=self.server_protocol,
                                  serverAuthToken=self.server_auth_token,
                                  clientId=self.client_id)
            # Write testcase content and any additional meta information to a temporary ZIP archive.
            buffer = StringIO.StringIO()
            zip_buffer = zipfile.ZipFile(buffer, 'w')
            for name, meta in self.bucket.items():
                zip_buffer.writestr(meta["name"], meta["data"])
            zip_buffer.close()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as testcase:
                buffer.seek(0)
                testcase.write(buffer.getvalue())
                testcase.close()
                # Submit crash report with testcase to FuzzManager.
                collector.submit(crash_info, testcase.name, metaData=None)
except Exception:
    logging.error("FuzzManager is deactivated!")

