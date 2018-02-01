import logging
import re


P_REQUEST_LOG = re.compile(r'^(.*?) - - \[(.*?)\] "(.*?)" (\d+) (\d+|-)$')

LOG = logging.getLogger('werkzeug')


def colorize_werkzeug():
    """
    Fetches the werkzeug logger and adds a color filter.

    This is based on "blessings". If it's not available, this is a no-op!
    """

    try:
        from blessings import Terminal
    except ImportError:
        return

    term = Terminal()
    method_colors = {
        'GET': term.bold_green,
        'POST': term.bold_yellow,
        'PUT': term.bold_blue,
        'DELETE': term.bold_red,
    }

    class WerkzeugColorFilter:

        def filter(self, record):
            match = P_REQUEST_LOG.match(record.msg)
            if match:
                try:
                    ip, date, request_line, status_code, size = match.groups()
                    method = request_line.split(' ')[0]  # key 0 always exists
                    fmt = method_colors.get(method.upper(), term.white)
                    request_line = fmt(request_line)
                    ip = term.blue(ip)
                    date = term.yellow(date)
                    try:
                        status_code_value = int(status_code)
                        if status_code_value >= 500:
                            status_code = term.yellow_on_red(status_code)
                        elif status_code_value >= 400:
                            status_code = term.red(status_code)
                        elif status_code_value >= 300:
                            status_code = term.black_on_yellow(status_code)
                        elif status_code_value >= 200:
                            status_code = term.green(status_code)
                        else:
                            status_code = term.bold_white(status_code)
                    except ValueError:
                        pass
                    record.msg = '%s - - [%s] "%s" %s %s' % (
                        ip, date, request_line, status_code, size
                    )
                except ValueError:
                    pass
            return record

    logging.getLogger('werkzeug').addFilter(WerkzeugColorFilter())