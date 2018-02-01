import logging
from twisted.python import log, failure


class TwistedLogHandler(logging.Handler):
    """
    Sends Python stdlib logging output through the Twisted logging system.
    """

    def __init__(self, twistedlogpublisher=None):
        logging.Handler.__init__(self)
        if twistedlogpublisher is None:
            twistedlogpublisher = log.theLogPublisher
        self.twistedlog = twistedlogpublisher

    def emit(self, record):
        try:
            info = vars(record)
            msg = self.format(record)
            info['isError'] = (record.levelno >= logging.ERROR)
            if record.exc_info is not None:
                t, v, tb = record.exc_info
                info['failure'] = failure.Failure(v, t, tb)
            info['message'] = record.msg
            self.twistedlog.msg(msg, **info)
        except Exception:
            self.handleError(record)
            

def usePythonLoggingWithTwisted(logger=None, level=None):
    if logger is None:
        logger = logging.getLogger()
    handler = TwistedLogHandler()
    if level != None:
        handler.setLevel(level)
    logger.addHandler(handler)