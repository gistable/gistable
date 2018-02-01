import requests
import json


class Diffbot(object):
    """
    A simple Python interface for the Diffbot api.
    Relies on the Requests library - python-requests.org

    Usage:
    YOUR_DIFFBOT_DEV_TOKEN = '12345'

    diffbot = Diffbot(YOUR_DIFFBOT_DEV_TOKEN)

    diffbot.get_article({
        'url': 'http://example.com/page',
    })

    diffbot.get_frontpage({
        'url': 'http://example.com',
    })

    """
    output_format = 'json'

    def __init__(self, dev_token):
        self.dev_token = dev_token

    def get_article(self, params={}):
        api_endpoint = 'http://www.diffbot.com/api/article'
        params.update({
            'token': self.dev_token,
            'format': self.output_format,
        })
        r = requests.get(api_endpoint, params=params)
        return json.loads(r.content)

    def get_frontpage(self, params={}):
        api_endpoint = 'http://www.diffbot.com/api/frontpage'
        params.update({
            'token': self.dev_token,
            'format': self.output_format,
        })
        r = requests.get(api_endpoint, params=params)
        return json.loads(r.content)
