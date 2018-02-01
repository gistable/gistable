
def slack_it(msg):
    ''' Send a message to a predefined slack channel.'''
    import urequests

    # Get an "incoming-webhook" URL from your slack account. @see https://api.slack.com/incoming-webhooks
    URL='https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'

    headers = {'content-type': 'application/json'}
    data = '{"text":"%s"}' % msg
    resp = urequests.post(URL, data=data, headers=headers)
    return resp

