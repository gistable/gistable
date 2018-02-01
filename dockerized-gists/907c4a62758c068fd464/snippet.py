"""
Example of making a request to JIRA as a trusted application.
In this example, we create a new issue as an arbitrary user.

More information on this technique at:
https://answers.atlassian.com/questions/247528/how-do-you-impersonate-a-user-with-jira-oauth
"""

import oauth2
import time
import requests
import json
import base64
from tlslite.utils import keyfactory


def oauth_sign(method, url, params, data, private_key_path):
    """Returns oauth_signature for a given request"""

    # Use oauth2 Request() to normalize the payload
    request = oauth2.Request(method, url, params, data)
    raw = '&'.join([
        oauth2.escape(request.method),
        oauth2.escape(request.normalized_url),
        oauth2.escape(request.get_normalized_parameters()),
    ])

    # Load the private keyfile
    with open(private_key_path, 'r') as f:
        privatekey = keyfactory.parsePrivateKey(f.read())

    # Calculate signature and return it as a b64-encoded string
    return base64.b64encode(privatekey.hashAndSign(raw))


def oauth_request(method, url, params, data, consumer_key, private_key_path):
    headers = {'content-type': 'application/json'}

    # Populate the oauth parameters
    params['oauth_consumer_key'] = consumer_key
    params['oauth_token'] = ''
    params['oauth_signature_method'] = 'RSA-SHA1'
    params['oauth_timestamp'] = int(time.time())
    params['oauth_nonce'] = oauth2.generate_nonce()

    # Calculate the signature (based on everything above)
    params['oauth_signature'] = oauth_sign(method, url, params, data, private_key_path)

    # Do the request and return the result
    return requests.request(method,
                            url,
                            params=params,
                            data=data,
                            headers=headers)


params = {
    'user_id': 'luke',
}

data = json.dumps({
    "fields": {
        "project": {
            "key": "TEST"
        },
        "issuetype": {
            "name": "Task"
        },
        "summary": "Testing OAuth"
    }
})


r = oauth_request(
    'POST',
    'https://jira.zymeworks.com/rest/api/2/issue',
    params,
    data,
    'zymevault-dev',
    'private.pem',
)

print r.text
