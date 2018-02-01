# This is a demo of how to authenticate with a Tent server
# Code taken from https://github.com/longears/python-tent-client
#   but shortened and cleaned up.
# It won't actually run as-is because I took out a lot of the
#   other code in __init__.
# It uses an ugly workflow requiring the user to cut and paste
#   parameters from the browser URL bar because we don't have
#   a webserver running that the server can use to give us
#   auth keys directly.

import requests
import macauthlib

class TentApp(object):
    def __init__(self)
        ...
        ... # see https://github.com/longears/python-tent-client/blob/master/tentapp.py
        ... # for the rest of this
        ...
        # where the server should send the keys during authentication
        self.oauthCallbackUrl = 'http://zzzzexample.com/oauthcallback'

        # these will be our auth keys
        self.appID = None
        self.mac_key_id = None
        self.mac_key = None

        # This session will later be replaced with one which
        # uses the auth keys for every request.
        # Start with a non-authenticated session
        self.session = requests.session() # start with a non-authenticated session

    def _authHook(self,req):
        # This method will be used as a "pre-request hook" for the requests session.
        # It does MAC Authentication using the macauthlib library.
        # It will hook up sign_request() to be called on every request
        # using the current value of self.mac_key_id and self.mac_key
        macauthlib.sign_request(req, id=self.mac_key_id, key=self.mac_key, hashmod=hashlib.sha256)
        return req

    def authenticate(self):
        # first, we register with the server to set
        #  self.appID, self.mac_key_id, self.mac_key
        # we will also makes a new self.session which uses MAC authentication
        # to be used for all future requests

        # describe our app to the server
        appInfoJson = {
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'icon': 'http://example.com/icon.png',
            'redirect_uris': [self.oauthCallbackUrl],
            'scopes': self.scopes
        }
        headers = {
            'Content-Type': 'application/vnd.tent.v0+json',
            'Accept': 'application/vnd.tent.v0+json',
        }
        requestUrl = self.apiRootUrls[0] + '/apps'
        # this is an unauthenticated request
        r = requests.post(requestUrl, data=json.dumps(appInfoJson), headers=headers)

        # get temporary key in response
        self.appID = r.json['id'].encode('utf-8')
        self.mac_key_id = r.json['mac_key_id'].encode('utf-8')
        self.mac_key = r.json['mac_key'].encode('utf-8')
        self.mac_algorithm = r.json['mac_algorithm'].encode('utf-8')

        # Set up a new session that uses MAC authentication.
        # This will be used for all future requests.
        # Right now this is using the temporary keys from the first half
        #  of the auth process.
        self.session = requests.session(hooks={"pre_request": self._authHook})

        # Send user to the server to grant access.
        # We will get the "code" in response.
        self.state = randomString()
        params = {
            'client_id': self.appID,
            'redirect_uri': self.oauthCallbackUrl,
            'state': self.state,
            'scope': ','.join(self.scopes.keys()),
            'tent_profile_info_types': 'all',
            'tent_post_types': 'all',
            'tent_notification_url': self.postNotificationUrl,
        }
        requestUrl = self.apiRootUrls[0] + '/oauth/authorize'
        urlWithParams = requestUrl + '?' + urlencode(params)

        print '---------------------------------------------------------\\'
        print
        print 'Opening web browser so you can grant access on your tent server.'
        print
        print 'After you grant access, your browser will be redirected to'
        print 'a nonexistant page.  Look in the url and find the "code"'
        print 'parameter.  Paste it here:'
        print
        print 'Example:'
        print 'http://zzzzexample.com/oauthcallback?code=15673b7718651a4dd53dc7defc88759e&state=ahyKV...'
        print '                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
        print
        webbrowser.open(urlWithParams)
        code = raw_input('> ')
        print
        print '---------------------------------------------------------/'

        # trade the code for permanent keys
        resource = '/apps/%s/authorizations'%self.appID
        jsonPayload = {'code':code, 'token_type':'mac'}
        headers = {
            'Content-Type': 'application/vnd.tent.v0+json',
            'Accept': 'application/vnd.tent.v0+json',
        }
        requestUrl = self.apiRootUrls[0] + resource
        # this session uses the temp keys we just got
        r = self.session.post(requestUrl, data=json.dumps(jsonPayload), headers=headers)

        # then get the response
        # now we have permanent keys
        # these will be used next time we use self.session to make a request
        self.mac_key_id = r.json['access_token'].encode('utf-8')
        self.mac_key = r.json['mac_key'].encode('utf-8')

        # now save the appID and keys locally for use next time
        # maybe write them to a config file or put them in a database