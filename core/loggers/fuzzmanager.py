# coding: utf-8
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import zipfile
import logging
import tempfile
try:
    from io import StringIO
except ImportError as msg:
    from StringIO import StringIO
try:
    import sys
    sys.path.append("utils/FuzzManager")
    from FTB.ProgramConfiguration import ProgramConfiguration
    from FTB.Signatures.CrashInfo import CrashInfo
    from Collector.Collector import Collector
except ImportError as msg:
    logging.warning("FuzzManager is missing or one of its dependencies: %s" % msg)

from ..logger import Logger


try:
    class FuzzManagerLogger(Logger):
        def __init__(self, **kwargs):
            super(FuzzManagerLogger, self).__init__()

            self.binary = None

            self.__dict__.update(kwargs)

            if not self.binary:
                raise Exception("Required FuzzManagerLogger setting 'binary' is missing.")

        def save_bucket_as_zip(self, bucket):
            """ Saves captured content of listeners as files to a zip archive.

            :param bucket: A dict in format of: {id: {name:'', data:''}}
            :return: The name of the zip archive.
            """
            buffer = StringIO()
            zip_buffer = zipfile.ZipFile(buffer, 'w')
            for name, meta in bucket.items():
                zip_buffer.writestr(meta["name"], meta["data"])
            zip_buffer.close()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as testcase:
                buffer.seek(0)
                testcase.write(buffer.getvalue())
                testcase.close()
                return testcase.name

        def add_fault(self):
            # Setup FuzzManager with target information and platform data.
            program_configuration = ProgramConfiguration.fromBinary(self.binary)

            # Prepare FuzzManager with crash information.
            stdout = "N/A"  # Todo: There is no plain stdout logger yet.
            stderr = "N/A"  # Todo: There is no plain stderr logger yet.
            auxdat = self.bucket.get("crashlog", "N/A").get("data", "N/A")
            metaData = None
            testcase = self.save_bucket_as_zip(self.bucket)
            crash_info = CrashInfo.fromRawCrashData(stdout, stderr, program_configuration, auxdat)

            # Submit crash report with testcase to FuzzManager.
            collector = Collector(tool="dharma")
            collector.submit(crash_info, testcase, metaData)
except Exception as msg:
    logging.error("FuzzManager is not available!")
