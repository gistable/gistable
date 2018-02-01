##!/usr/bin/env python
# -*- coding: utf-8 -*-
"""yggdrasil.py

A tool for debugging and exploring yggdrasil, Minecraft's new
authentication system.

Usage:
    yggdrasil.py login <username> [--password=<password>]
    yggdrasil.py migrated <username>
"""
import sys
import json
import getpass

import requests
from docopt import docopt

_BASE = 'https://authserver.mojang.com/'


class YggdrasilException(Exception):
    def __init__(self, errorMessage, error, cause=None):
        Exception.__init__(self, errorMessage)
        self.error = error
        self.cause = cause


def _response_or_error(j):
    if 'error' in j:
        raise YggdrasilException(
            j.get('errorMessage'),
            j.get('error'),
            cause=j.get('cause')
        )
    return j


class Yggdrasil(object):
    #: The latest known valid agent name.
    LATEST_AGENT_NAME = 'minecraft'
    #: The latest known valid agent version.
    LATEST_AGENT_VERSION = 1

    class Endpoints(object):
        #: API URL for authentication.
        AUTHENTICATE = _BASE + 'authenticate'
        REFRESH = _BASE + 'refresh'
        VALIDATE = _BASE + 'valdiate'
        INVALIDATE = _BASE + 'invalidate'
        SIGNOUT = _BASE + 'signout'

    def __init__(self, agent_name=None, agent_version=None):
        self._agent_name = agent_name or self.LATEST_AGENT_NAME
        self._agent_version = agent_version or self.LATEST_AGENT_VERSION

        self._username = None
        self._access_token = None
        self._available_profiles = []
        self._client_token = None
        self._selected_profile = None

    @property
    def username(self):
        return self._username

    @property
    def access_token(self):
        return self._access_token

    @property
    def available_profiles(self):
        return self._available_profiles

    @property
    def selected_profile(self):
        return self._selected_profile

    @property
    def client_token(self):
        return self._client_token

    @property
    def session_token(self):
        return 'token:{token}:{id}'.format(
            token=self._access_token,
            id=self._selected_profile['id']
        )

    def login(self, username, password):
        """
        Login this Yggdrasil client using `username` and `password`.

        :param username: The username for the account.
        :param password: The password for the account.
        :returns: ``True`` if the login was successful.
        :rtype: bool.
        """
        self._username = username

        j = Yggdrasil._login_request(username, password, {
            'name': self._agent_name,
            'version': self._agent_version
        })

        self._access_token = j['accessToken']
        self._available_profiles = j.get('availableProfiles')
        self._client_token = j['clientToken']
        self._selected_profile = j.get('selectedProfile')

        return True

    def logout(self):
        """
        Logs the client out.
        """
        Yggdrasil._logout_request(self.access_token, self.client_token)
        return True

    def switch_profile(self, profile):
        """
        Refreshes the active account profile.

        :param profile: The profile to switch to.
        """
        j = Yggdrasil._refresh_request(
            self.access_token,
            self.client_token,
            profile
        )

        self._access_token = j['accessToken']
        self._client_token = j['clientToken']
        self._available_profiles = j['availableProfiles']
        self._selected_profile = j['selectedProfile']

        return True

    @classmethod
    def _refresh_request(cls, access_token, client_token, profile):
        r = requests.post(cls.Endpoints.REFRESH, data=json.dumps({
            'accessToken': access_token,
            'clientToken': client_token,
            'profile': profile
        }))

        return _response_or_error(r.json())

    @classmethod
    def _login_request(cls, username, password, agent):
        r = requests.post(cls.Endpoints.AUTHENTICATE, data=json.dumps({
            'username': username,
            'password': password,
            'agent': agent
        }))

        return _response_or_error(r.json())

    @classmethod
    def _logout_request(cls, access_token, client_token):
        r = requests.post(cls.Endpoints.INVALIDATE, data=json.dumps({
            'acessToken': access_token,
            'clientToken': client_token
        }))

        return _response_or_error(r.json())

    def account_migrated(self, username):
        """
        Checks to see if the account by the username `username`
        has been migrated to a Mojang account.

        :param username: The username to check.
        :returns: ``True`` if migrated, ``False`` otherwise.
        :rtype: bool
        """
        try:
            Yggdrasil._login_request(username, '-1', {
                'name': self._agent_name,
                'version': self._agent_version
            })
        except YggdrasilException as e:
            if e.cause == 'UserMigratedException':
                return True
            return False
        else:
            return False


def main(argv):
    args = docopt(__doc__, argv=argv[1:])

    client = Yggdrasil()

    if args['login']:
        password = args['--password'] or getpass.getpass('Password > ')
        client.login(args['<username>'], password)
    elif args['migrated']:
        print(client.account_migrated(args['<username>']))


if __name__ == '__main__':
    sys.exit(main(sys.argv))
