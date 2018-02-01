import subprocess
import select
from logging import DEBUG, ERROR


def call(popenargs, logger, stdout_log_level=DEBUG, stderr_log_level=ERROR, **kwargs):
    """
    Variant of subprocess.call that accepts a logger instead of stdout/stderr,
    and logs stdout messages via logger.debug and stderr messages via
    logger.error.
    """
    child = subprocess.Popen(popenargs, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, **kwargs)

    log_level = {child.stdout: stdout_log_level,
                 child.stderr: stderr_log_level}

    def check_io():
        ready_to_read = select.select([child.stdout, child.stderr], [], [], 1000)[0]
        for io in ready_to_read:
            line = io.readline()
            logger.log(log_level[io], line[:-1])

    # keep checking stdout/stderr until the child exits
    while child.poll() is None:
        check_io()

    check_io()  # check again to catch anything after the process exits

    return child.wait()


# tests, plunked in here for convenience

import sys
import unittest2
import logging_subprocess
import logging
from StringIO import StringIO


class LoggingSubprocessTest(unittest2.TestCase):
    def setUp(self):
        self.buffer = StringIO()
        self.logger = logging.getLogger('logging_subprocess_test')
        self.logger.setLevel(logging.DEBUG)
        self.logHandler = logging.StreamHandler(self.buffer)
        formatter = logging.Formatter("%(levelname)s-%(message)s")
        self.logHandler.setFormatter(formatter)
        self.logger.addHandler(self.logHandler)

    def test_log_stdout(self):
        logging_subprocess.call([sys.executable, "-c",
                                "print 'foo'"], self.logger)
        self.assertIn('DEBUG-foo', self.buffer.getvalue())

    def test_log_stderr(self):
        logging_subprocess.call([sys.executable, "-c",
                                'import sys; sys.stderr.write("foo\\n")'],
                                self.logger)
        self.assertIn('ERROR-foo', self.buffer.getvalue())

    def test_custom_stdout_log_level(self):
        logging_subprocess.call([sys.executable, "-c",
                                "print 'foo'"], self.logger,
                                stdout_log_level=logging.INFO)
        self.assertIn('INFO-foo', self.buffer.getvalue())

    def test_custom_stderr_log_level(self):
        logging_subprocess.call([sys.executable, "-c",
                                'import sys; sys.stderr.write("foo\\n")'],
                                self.logger,
                                stderr_log_level=logging.WARNING)
        self.assertIn('WARNING-foo', self.buffer.getvalue())

if __name__ == "__main__":
    unittest2.main()
