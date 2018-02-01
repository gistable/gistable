__author__ = 'youngsoul'


import time
import random
from string import Template
import urllib2

"""
Dev Note:
import json does not work and I could not find a way to include a json package.  Fortunately
it is a string json payload so I did not technically need it.
opkg update
opkg install python-light
opkg install python-logging
opkg install python-openssl

Gist: https://gist.github.com/youngsoul/c38287599b0e2fd743f2
"""

# https://gist.github.com/logic/2715756
# req = MethodRequest(url, method='PUT')
class MethodRequest(urllib2.Request):
    def __init__(self, *args, **kwargs):
        if 'method' in kwargs:
            self._method = kwargs['method']
            del kwargs['method']
        else:
            self._method = None
        return urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self, *args, **kwargs):
        if self._method is not None:
            return self._method
        return urllib2.Request.get_method(self, *args, **kwargs)


lights_url_template = """http://192.168.100.53/api/pryan-sparky/lights/$light_number/state"""

light_payload_template = """{"on": true, "sat": $sat_value, "bri": $bri_value, "hue": $hue_value}"""

light_off = """{"on": false}"""


def put(url, data, params=None, headers=None):
    if headers is None:
        headers = {}
    headers['Content-Type'] = 'application/json'
    if params is None:
        params = {}

    if data is None:
        data = {}

    pay_load = data

    req = MethodRequest(url, data=data, headers=headers, method='PUT')
    response = urllib2.urlopen(req)
    the_data = response.read()

    return

if __name__ == '__main__':

    try:
        while True:
            sat_value = random.randint(1,255)
            bri_value = 255  #random.randint(1,255)
            hue_value = random.randint(1,38948)
            light_value = 6

            light_url = Template(lights_url_template).substitute(light_number=str(light_value))

            json_payload = Template(light_payload_template).substitute(sat_value=str(sat_value), bri_value=str(bri_value), hue_value=str(hue_value))
            put(light_url, json_payload)

            time.sleep(3)
    except:
        time.sleep(10)
