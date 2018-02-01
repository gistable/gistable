"""
Example for a colourised logging output.

This example uses "blessings" to handle console escape sequences. ``blessings``
itself is a very harmless package in that it does not have any external
dependencies. And it's code-base is very clean and small.

The example extends the core logging formatter (logging.Formatter) and
colourises the complete line. This takes advantage of any upstream updates
related to logging. When writing this against Python 2.7, the parent code
already contains some very specific optimisation and error handling! If you
want to colourise the individual fields, do so at your own risk!

In a production environment I would like to have everything with a level ≥
``logging.WARNING`` sent to stderr instead of stdout, which can be done with a
``Filter``, but that's not the purpose of this example!
"""

import sys
import logging
import logging.handlers

from blessings import Terminal

LOG = logging.getLogger(__name__)


class ColoredFormatter(logging.Formatter):

    def __init__(self, terminal, *args, **kwargs):
        super(ColoredFormatter, self).__init__(*args, **kwargs)
        self._terminal = terminal

    def format(self, record):
        output = super(ColoredFormatter, self).format(record)
        if record.levelno >= logging.CRITICAL:
            line_color = self._terminal.bold_yellow_on_red
        elif record.levelno >= logging.ERROR:
            line_color = self._terminal.red
        elif record.levelno >= logging.WARNING:
            line_color = self._terminal.yellow
        elif record.levelno >= logging.INFO:
            line_color = self._terminal.green
        else:
            line_color = self._terminal.white
        return line_color(output)


if __name__ == '__main__':
    terminal = Terminal()
    clifmt = ColoredFormatter(
        terminal,
        '%(asctime)s [%(threadName)s] %(levelname)-10s %(message)s')
    root_logger = logging.getLogger()
    clihandler = logging.StreamHandler(sys.stdout)
    clihandler.setFormatter(clifmt)
    root_logger.setLevel(logging.NOTSET)
    root_logger.addHandler(clihandler)

    LOG.debug('Debug message')
    LOG.info('Info message')
    LOG.warning('Warning message')
    LOG.error('Error message')
    LOG.exception('Exception message')
    LOG.critical('Critical message')
