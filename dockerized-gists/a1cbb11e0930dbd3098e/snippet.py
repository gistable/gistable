import os, inspect

class Push:
    """A simple wrapper around Pushbullet"""

    def __init__(self, key):
        self.key = key
        self.title = inspect.stack()[1][1]

    def post(self, msg, title=None):
        title = title or self.title
        os.system('curl -u %s: -X POST https://api.pushbullet.com/v2/pushes --header \'Content-Type: application/json\' --data-binary \'{"type":"note", "title": "%s", "body": "%s"}\'' % (self.key, title, msg))

    def warn(self, msg, title=None):
        self.post('Warning: %s' % msg, title)

    def notify(self, msg, title=None):
        self.post('Notification: %s' % msg, title)

    def error(self, msg, title=None):
        self.post('Error: %s' % msg, title)
