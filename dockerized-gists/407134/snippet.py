#!/usr/bin/env python

"""
This module provides an interface to the Google Prediction API.
"""

import json
import numbers
import urllib
import urllib2
import urlparse

def get_auth(email, password):
    """
    Retrieves a Google authentication token.
    """

    url = 'https://www.google.com/accounts/ClientLogin'

    post_data = urllib.urlencode([
        ('Email', email),
        ('Passwd', password),
        ('accountType', 'HOSTED_OR_GOOGLE'),
        ('source', 'companyName-applicationName-versionID'),
        ('service', 'xapi'),
    ])

    request = urllib2.Request(url, post_data)
    response = urllib2.urlopen(request)

    content = '&'.join(response.read().split())
    query = urlparse.parse_qs(content)
    auth = query['Auth'][0]

    response.close()

    return auth

def train(auth, model):
    """
    Tells the Google Prediction API to train the supplied model.
    """

    url = 'https://www.googleapis.com/prediction/v1/training?data=%s' % \
        urllib.quote(model, '')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'GoogleLogin auth=%s' % auth,
    }

    post_data = json.dumps({
        'data': {},
    })

    request = urllib2.Request(url, post_data, headers)
    response = urllib2.urlopen(request)
    response.close()

def predict(auth, model, query):
    """
    Makes a prediction based on the supplied model and query data.
    """

    url = 'https://www.googleapis.com/prediction/v1/training/%s/predict' % \
        urllib.quote(model, '')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'GoogleLogin auth=%s' % auth,
    }

    data_input = {}

    if isinstance(query, basestring):
        data_input['text'] = [query]
    elif isinstance(query, numbers.Number):
        data_input['numeric'] = [query]

    post_data = json.dumps({
        'data': {
            'input': data_input
        }
    })

    request = urllib2.Request(url, post_data, headers)
    response = urllib2.urlopen(request)

    content = response.read()
    prediction = json.loads(content)['data']['output']['output_label']

    response.close()

    return prediction

def main():
    """
    Asks for the user's Google credentials, Prediction API model and queries.
    """

    from getpass import getpass

    google_email = raw_input('Email: ')
    google_password = getpass('Password: ')
    auth = get_auth(google_email, google_password)

    message = 'Enter text for classification. Hit control-c to quit: '
    model = raw_input('Model: ')
    while True:
        query = raw_input(message)
        print predict(auth, model, query)

if __name__ == '__main__':
    main()
