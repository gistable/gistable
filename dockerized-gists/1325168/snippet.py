import requests
import json


class ClickyApi(object):
    """
    A simple Python interface for the Clicky web analytics api.
    Relies on the Requests library - python-requests.org

    Usage:
    YOUR_CLICKY_SITE_ID = '12345'
    YOUR_CLICKY_SITE_KEY = 'qwerty'

    clicky = ClickyApi(YOUR_CLICKY_SITE_ID, YOUR_CLICKY_SITE_KEY)

    clicky.stats({
        'type': 'pages',
        'date': 'today'
    })

    """
    api_endpoint = 'http://api.getclicky.com/api/stats/4'
    output_format = 'json'
    site_id = ''
    site_key = ''

    def __init__(self, site_id, site_key, app=''):
        self.site_id = site_id
        self.site_key = site_key
        self.app = app

    def stats(self, params={}):
        params.update({
            'site_id': self.site_id,
            'sitekey': self.site_key,
            'output': self.output_format,
            'app': self.app
        })
        r = requests.get(self.api_endpoint, params=params)
        return json.loads(r.content)
