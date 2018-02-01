import datetime
import logging
import requests
import urlparse

class JamfUAPIAuthToken(object):
    def __init__(self, jamf_url, username, password):
        """
        :param jamf_url: Jamf Pro URL
        :type jamf_url: str
        :param username: Username for authenticating to JSS
        :param password: Password for the provided user
        """
        split = urlparse.urlsplit(jamf_url)
        self.server_url = self._base_url(
            'https' if not split.scheme else split.scheme,
            split.netloc if split.netloc else split.path
        )
        self._auth = (username, password)
        self._token = ''
        self._token_expires = float()

        self.get_token()

    @staticmethod
    def unix_timestamp():
        """Returns a UTC Unix timestamp for the current time"""
        epoch = epoch = datetime.datetime(1970, 1, 1)
        now = datetime.datetime.utcnow()
        return (now - epoch).total_seconds()

    @staticmethod
    def _base_url(scheme, server):
        return urlparse.urlunsplit((scheme, server, 'uapi', None, None))

    def build_url(self, path):
        base_url = urlparse.urlsplit(self.server_url)
        api_path = '/'.join((base_url.path.strip('/'), path)) if path else base_url.path
        return urlparse.urlunsplit((base_url.scheme, base_url.netloc, api_path, '', ''))

    def headers(self, add=None):
        """
        :param add: Dictionary of headers to add to the default header
        :type add: dict
        """
        header = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        if hasattr(self, '_auth_token'):
            header.update(self._auth_token.header)

        if add:
            header.update(add)

        return header

    @property
    def token(self):
        if (self._token_expires - self.unix_timestamp()) < 0:
            logging.warning("JSSAuthToken has expired: Getting new token")
            self.get_token()
        elif (self._token_expires - self.unix_timestamp()) / 60 < 5:
            logging.info("JSSAuthToken will expire soon: Refreshing")
            self.refresh_token()

        return self._token

    @token.setter
    def token(self, new_token):
        self._token = new_token

    @property
    def header(self):
        return {'Authorization': 'jamf-token {}'.format(self.token)}

    def __repr__(self):
        return "<JSSAuthToken(username='{}')>".format(self._auth[0])

    def get_token(self):
        url = self.build_url('auth/tokens')
        logging.info("JSSAuthToken requesting new token")
        response = requests.post(url, auth=self._auth)
        if response.status_code != 200:
            raise Exception

        self._set_token(response.json()['token'], response.json()['expires'])

    def refresh_token(self):
        url = self.build_url('auth/keepAlive')
        logging.info("JSSAuthToken attempting to refresh existing token")
        response = requests.post(url, headers=self.headers())
        if response.status_code != 200:
            logging.warning("JSSAuthToken is expired: Getting new token")
            self.get_token()

        self._set_token(response.json()['token'], response.json()['expires'])

    def _set_token(self, token, expires):
        """
        :param token:
        :type token: str
        :param expires:
        :type expires: int
        """
        self.token = token
        self._token_expires = float(expires) / 1000

    def about_token(self):
        url = self.build_url('auth')
        response = requests.get(url, headers=self.headers())
        return response.json()
