from logging import handlers
import logging
from tornado import ioloop, web

MAX_SIZE = 10485760  # 10 MB


class BufferedLogHandler(handlers.BufferingHandler):
    """The BufferedLogHandler keeps a rolling buffer of log data in
    memory. When the buffer size has been exceeded, the oldest log
    entries will be removed.

    The max buffer size is passed into the constructor. See the
    logging.handlers.BufferingHandler for the full API.

    Access the log data as a list from the BufferedLogHandler.buffer
    attribute

    """
    def emit(self, record):
        """Append the formatted record to the buffer, removing oldest
        entries if the buffer size has passed the limit.

        :param logging.LogRecord record: The new record to log

        """
        self.buffer.append(self.format(record))
        while len(self.buffer) >= self.capacity:
            self.buffer.remove(0)


class WebRequestHandler(web.RequestHandler):
    """Tornado request handler that emits the BufferedLogHandler's
    buffer content in JSON format when GET was invoked. If flush
    is passed as a query value, the buffer will be flushed:

    /?flush=true

    """
    def get(self):
        """Return a JSON document of the log entries and flush the
        BufferedLogHandler if there is a flush argument in the URL.

        """
        handler = self.application.log_handler
        self.write({'log_entries': handler.buffer})
        if self.get_argument('flush', False):
            handler.flush()


if __name__ == '__main__':

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Create the web application
    routes = [(r'.*', WebRequestHandler)]
    application = web.Application(routes)
    application.listen(8888)

    # Create the log handler
    application.log_handler = BufferedLogHandler(MAX_SIZE)

    # Add the log handler to the root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(application.log_handler)

    # Start the IOLoop
    ioloop.IOLoop.instance().start()
