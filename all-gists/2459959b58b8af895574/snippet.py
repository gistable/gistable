from __future__ import print_function
import logging
import sys

class ShutdownHandler(logging.Handler):
    def emit(self, record):
        print(record.msg, file=sys.stderr)
        logging.shutdown()
        sys.exit(1)

logging.getLogger().addHandler(ShutdownHandler(level=50))