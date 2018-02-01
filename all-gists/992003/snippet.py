import optparse
import logging
import sys

log = logging.getLogger("your-logger")

# Usual logging boilerplate, unnecessary in Python >= 3.1.
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record): pass
log.addHandler(NullHandler())

# Most of your logic and stuff goes here.

def main()
    parser = optparse.OptionParser()
    parser.add_option("-v", dest="verbose", default=0, action="count",
            help="increment output verbosity; may be specified multiple times")

    # For each -v passed on the commandline, a lower log.level will be enabled.
    # log.ERROR by default, log.INFO with -vv, etc.
    log.addHandler(logging.StreamHandler())
    log.level = max(logging.ERROR - (opts.verbose * 10), 1)

if __name__ == "__main__":
    try:
        ret = main()
    except KeyboardInterrupt:
        ret = None
    sys.exit(ret)
