# -*- coding: utf-8 -*-
# Based on https://github.com/ikasamah/withings-garmin/blob/master/withings.py

import urllib
from datetime import datetime
import urlparse
import oauth2 as oauth

try:
    import json
except ImportError:
    import simplejson as json


class WithingsException(Exception):
    pass


class WithingsAPIError(WithingsException):
    DESCRIPTIONS = {
        100: 'The hash is missing, invalid, or does not match the provided email',
        247: 'The userid is absent, or incorrect',
        250: 'The userid and publickey do not match, or the user does not share its data',
        264: 'The email address provided is either unknown or invalid',
        286: 'No such subscription was found',  # ?
        293: 'The callback URL is either absent or incorrect',
        294: 'No such subscription could be deleted',
        304: 'The comment is either absent or incorrect',
        2555: 'An unknown error occured',
    }

    def __init__(self, status=2555):
        self.status = status
        self.message = self.DESCRIPTIONS.get(status, 'unknown status')


class WithingsClient(object):
    BASE_URL          = 'http://wbsapi.withings.net/'
    REQUEST_TOKEN_URL = 'https://oauth.withings.com/account/request_token'
    ACCESS_TOKEN_URL  = 'https://oauth.withings.com/account/access_token'
    AUTHORIZE_URL     = 'https://oauth.withings.com/account/authorize'

    def __init__(self, consumer_key, consumer_secret, oauth_token=None, oauth_token_secret=None, userid=None):
        self.consumer = oauth.Consumer(consumer_key, consumer_secret)
        if oauth_token:
            token = oauth.Token(oauth_token, oauth_token_secret)
            self.client = oauth.Client(self.consumer, token)
        else:
            self.client = oauth.Client(self.consumer)
        self.id = userid

    # Step 1
    def get_request_token(self, callback):
        resp, content = self.client.request(WithingsClient.REQUEST_TOKEN_URL, 'POST', body=urllib.urlencode({'oauth_callback': callback}))
        if resp['status'] != 200:
            raise Exception("Invalid response %s." % resp['status'])
        request_token = dict(urlparse.parse_qsl(content))
        return request_token
    
    # Step 2
    def get_authorization_url(self, request_token):
        return '%s?oauth_token=%s' % (WithingsClient.AUTHORIZE_URL, request_token['oauth_token'])

    # Step 3
    def get_access_token(self, oauth_verifier):
        resp, content = self.client.request('%s?oauth_verifier=%s' % (WithingsClient.ACCESS_TOKEN_URL, oauth_verifier), 'POST')
        access_token = dict(urlparse.parse_qsl(content))
        if resp['status'] != 200 or 'oauth_token' not in access_token:
            raise Exception('Invalid oauth response from Withings')
        token = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])
        self.client = oauth.Client(self.consumer, token)
        return access_token

    def call(self, service, action, params=None):
        url = self.build_url(service, action, params)
        resp, content = self.client.request(url, 'GET')
        if resp['status'] != 200:
            raise Exception('API didnt return 200 response.')
        try:
            json_response = json.loads(content)
        except ValueError:
            raise WithingsException('API did not return valid json response.')
        status = json_response['status']
        if (status != 0):
            raise WithingsAPIError(status)
        return json_response.get('body')

    def build_url(self, service, action, params=None):
        url = '%s%s?action=%s' % (WithingsClient.BASE_URL, service, action)
        if params:
            if isinstance(params, dict):
                params = dict((k, v) for k, v in params.items() if v is not None)
                params = urllib.urlencode(params)
            url = '%s&%s' % (url, params)
        return url

    def get_measurements(self, *args, **kwargs):
        defaults = {'userid': self.id}
        defaults.update(kwargs)
        response = self.call('measure', 'getmeas', defaults)
        return [WithingsMeasureGroup(g) for g in response['measuregrps']]

    def add_subscription(self, *args, **kwargs):
        defaults = {'userid': self.id}
        defaults.update(kwargs)
        response = self.call('notify', 'subscribe', defaults)
        return response

    def remove_subscription(self, *args, **kwargs):
        defaults = {'userid': self.id}
        defaults.update(kwargs)
        response = self.call('notify', 'revoke', defaults)
        return response


class WithingsMeasureGroup(object):
    def __init__(self, measuregrp):
        self._raw_data = measuregrp
        self.id = measuregrp.get('grpid')
        self.attrib = measuregrp.get('attrib')
        self.date = measuregrp.get('date')
        self.category = measuregrp.get('category')
        self.measures = [WithingsMeasure(m) for m in measuregrp['measures']]

    def __iter__(self):
        for measure in self.measures:
            yield measure

    def __len__(self):
        return len(self.measures)

    def get_datetime(self):
        return datetime.fromtimestamp(self.date)

    def get_weight(self):
        """Utility function to get weight"""
        for measure in self.measures:
            if measure.type == WithingsMeasure.TYPE_WEIGHT:
                return measure.get_value()
        return None

    def get_fat_ratio(self):
        """Utility function to get fat ratio"""
        for measure in self.measures:
            if measure.type == WithingsMeasure.TYPE_FAT_RATIO:
                return measure.get_value()
        return None


class WithingsMeasure(object):
    TYPE_WEIGHT = 1
    TYPE_HEIGHT = 4
    TYPE_FAT_FREE_MASS = 5
    TYPE_FAT_RATIO = 6
    TYPE_FAT_MASS_WEIGHT = 8

    def __init__(self, measure):
        self._raw_data = measure
        self.value = measure.get('value')
        self.type = measure.get('type')
        self.unit = measure.get('unit')

    def __str__(self):
        type_s = 'unknown'
        unit_s = ''
        if (self.type == self.TYPE_WEIGHT):
            type_s = 'Weight'
            unit_s = 'kg'
        elif (self.type == self.TYPE_HEIGHT):
            type_s = 'Height'
            unit_s = 'meter'
        elif (self.type == self.TYPE_FAT_FREE_MASS):
            type_s = 'Fat Free Mass'
            unit_s = 'kg'
        elif (self.type == self.TYPE_FAT_RATIO):
            type_s = 'Fat Ratio'
            unit_s = '%'
        elif (self.type == self.TYPE_FAT_MASS_WEIGHT):
            type_s = 'Fat Mass Weight'
            unit_s = 'kg'
        return '%s: %s %s' % (type_s, self.get_value(), unit_s)

    def get_value(self):
        return self.value * pow(10, self.unit)