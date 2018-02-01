import sys
import urllib
import urllib2
import json
import logging


class GeonamesError(Exception):
    
    def __init__(self, status):
        Exception.__init__(self, status)        # Exception is an old-school class
        self.status = status
    
    def __str__(self):
        return self.status
    
    def __unicode__(self):
        return unicode(self.__str__())


class GeonamesClient(object):
    BASE_URL = 'http://api.geonames.org/'

    def __init__(self, username):
        self.username = username

    def call(self, service, params=None):
        url = self.build_url(service, params)

        try:
            response = urllib2.urlopen(urllib2.Request(url))
            json_response = json.loads(response.read())
        except urllib2.URLError, e:
            raise GeonamesError('API didnt return 200 response.')
        except ValueError:
            raise GeonamesError('API did not return valid json response.')
        else:
            if 'status' in json_response:
                raise GeonamesError(json_response['status']['message'])
        return json_response

    def build_url(self, service, params=None):
        url = '%s%s?username=%s' % (GeonamesClient.BASE_URL, service, self.username)
        if params:
            if isinstance(params, dict):
                params = dict((k, v) for k, v in params.items() if v is not None)
                params = urllib.urlencode(params)
            url = '%s&%s' % (url, params)
        return url
    
    # http://api.geonames.org/timezoneJSON?lat=47.01&lng=10.2&username=demo
    def find_timezone(self, params):
        return self.call('timezoneJSON', params)