#coding: utf-8

import json

import requests


class Slack(object):
    """
    References:
    ==========
      * Incoming Webkooks: https://api.slack.com/
      * Bootstrap Colors: http://getbootstrap.com/css/#less-variables
    """
    
    PRIMARY = '#428bca'         # Blue
    SUCCESS = '#5cb85c'         # Green
    INFO    = '#5bc0de'         # Light blue
    WARNING = '#f0ad4e'         # Orange
    DANGER  = '#d9534f'         # Red
    
    def __init__(self, webhook_url, channel=None):
        self.webhook_url = webhook_url
        self.channel = channel

    
    def _send(self, data):
        msg = {}
        if self.channel:
            msg['channel'] = self.channel
        msg.update(data)
        return requests.post(self.webhook_url, data=json.dumps(msg))

    def send(self, message):
        return self._send({"text": message})

    def send_rich(self, pretext, color, fields, fallback=None):
        """
        :param color: Slack.{PRIMARY, SUCCESS, INFO, WARNING, DANGER}
        :param fields: list of {"title": "", "value": ""}
        """
        return self._send({
            "attachments": [{
                "fallback": fallback if fallback else pretext,
                "pretext": pretext,
                "color": color,
                "fields": fields
            }]
        })