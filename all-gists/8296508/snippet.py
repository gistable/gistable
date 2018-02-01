"""
HTML logger inspired by the Horde3D logger.

Usage:

 - call setup and specify the filename, title, version and level
 - call dbg, info, warn or err to log messages.
"""
import logging
import time

#: HTML header (starts the document
_START_OF_DOC_FMT = """<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>%(title)s</title>
<style type="text/css">
body, html {
background: #000000;
width: 1000px;
font-family: Arial;
font-size: 16px;
color: #C0C0C0;
}
h1 {
color : #FFFFFF;
border-bottom : 1px dotted #888888;
}
pre {
font-family : arial;
margin : 0;
}
.box {
border : 1px dotted #818286;
padding : 5px;
margin: 5px;
width: 950px;
background-color : #292929;
}
.err {
color: #EE1100;
font-weight: bold
}
.warn {
color: #FFCC00;
font-weight: bold
}
.info {
color: #C0C0C0;
}
.debug {
color: #CCA0A0;
}
</style>
</head>

<body>
<h1>%(title)s</h1>
<h3>%(version)s</h3>
<div class="box">
<table>
"""

_END_OF_DOC_FMT = """</table>
</div>
</body>
</html>
"""

_MSG_FMT = """
<tr>
<td width="100">%(time)s</td>
<td class="%(class)s"><pre>%(msg)s</pre></td>
<tr>
"""


class HTMLFileHandler(logging.FileHandler):
    """
    File handler specialised to write the start of doc as html and to close it
    properly.
    """
    def __init__(self, title, version, *args):
        super().__init__(*args)
        assert self.stream is not None
        # Write header
        self.stream.write(_START_OF_DOC_FMT % {"title": title,
                                    "version": version})

    def close(self):
        # finish document
        self.stream.write(_END_OF_DOC_FMT)
        super().close()


class HTMLFormatter(logging.Formatter):
    """
    Formats each record in html
    """
    CSS_CLASSES = {'WARNING': 'warn',
                   'INFO': 'info',
                   'DEBUG': 'debug',
                   'CRITICAL': 'err',
                   'ERROR': 'err'}

    def __init__(self):
        super().__init__()
        self._start_time = time.time()

    def format(self, record):
        try:
            class_name = self.CSS_CLASSES[record.levelname]
        except KeyError:
            class_name = "info"

        t = time.time() - self._start_time
        
        # handle '<' and '>' (typically when logging %r)
        msg = record.msg
        msg = msg.replace("<", "&#60")
        msg = msg.replace(">", "&#62")

        return _MSG_FMT % {"class": class_name, "time": "%.4f" % t,
                       "msg": msg}


class HTMLLogger(logging.Logger):
    """
    Log records to html using a custom HTML formatter and a specialised
    file stream handler.
    """
    def __init__(self,
                 name="html_logger",
                 level=logging.DEBUG,
                 filename="log.html", mode='w',
                 title="HTML Logger", version="1.0.0"):
        super().__init__(name, level)
        f = HTMLFormatter()
        h = HTMLFileHandler(title, version, filename, mode)
        h.setFormatter(f)
        self.addHandler(h)


#: Global logger instance
_logger = None


def setup(title, version, filename="log.html", mode='w', level=logging.DEBUG):
    """
    Setup the logger

    :param title: Title of the html document
    :param version: Framework/lib/app version
    :param filename: output filename. Default is "log.html"
    :param mode: File open mode. Default is 'w'
    :param level: handler output level. Default is DEBUG
    """
    global _logger
    if _logger is None:
        _logger = HTMLLogger(filename=filename, mode=mode, title=title,
                             version=version, level=level)


def dbg(msg):
    """
    Logs a debug message
    """
    global _logger
    _logger.debug(msg)


def info(msg):
    """
    Logs an info message
    """
    global _logger
    _logger.info(msg)


def warn(msg):
    """
    Logs a warning message
    """
    global _logger
    _logger.warning(msg)


def err(msg):
    """
    Logs an error message
    """
    global _logger
    _logger.error(msg)


# Example of usage
if __name__ == "__main__":
    setup("Example", "1.0")
    dbg("A debug message")
    info("An information message")
    warn("A warning message")
    time.sleep(1)
    err("An error message")