# A simple log filter to turn debug logging on and off on a per-module
# basis, when using tornado-style logging.  Note that this works based
# on the module where the log statement occurs, not the name passed to
# logging.getLogger(), so it works even with libraries write directly
# to the root logger.
#
# One drawback to this approach (as opposed to using distinct
# per-module loggers and setting their levels appropriately) is that
# logger.isEnabledFor(DEBUG) will return true even when called from a
# module where debug output is not enabled, so modules that perform
# expensive logging only when debug logging is enabled may have degraded
# performance.
import logging
from tornado.options import parse_command_line, define, options

define('debug_module', type=str, multiple=True, default=[],
       help='list of module names that should log debug output')

class DebugModuleFilter(logging.Filter):
    def __init__(self):
        logging.Filter.__init__(self)
        self.debug_modules = set(options.debug_module)

    def filter(self, record):
        # This filter assumes that we want INFO logging from all
        # modules and DEBUG logging from only selected ones, but
        # easily could be adapted for other policies.
        if record.levelno == logging.DEBUG:
            return record.module in self.debug_modules
        return True

def main():
    parse_command_line()

    if options.debug_module:
        # The logger's level setting causes log entries to be discarded
        # before reaching our filter, so we must set the level to the
        # lowest level we want from any module.
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger().addFilter(DebugModuleFilter())

if __name__ == '__main__':
    main()
