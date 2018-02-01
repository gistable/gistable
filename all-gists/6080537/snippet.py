import os
import errno

SUITE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'suites')

try:
    os.makedirs(SUITE_PATH)
except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise