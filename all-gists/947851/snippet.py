"""
WiFi Positioning System

Wrappers around the SkyHook and Google Locations APIs to resolve
wireless routers' MAC addresses (BSSID) to physical locations.
"""
try:
    from json       import dumps, loads
except:
    from simplejson import dumps, loads
from urllib2    import Request, urlopen
from urllib     import urlencode

class GoogleLocation:
    
    def __init__(self):
        self.url = 'http://www.google.com/loc/json'
    
    def locate(self, mac):
        data = {
            'version': '1.1.0',
            'request_address': True,
            'wifi_towers': [{
                'mac_address': mac,
                'ssid': 'g',
                'signal_strength': -72
            }]
        }
        response = urlopen(self.url, dumps(data))
        return response.read()