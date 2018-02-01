import urllib, urllib2, json

'''
The ``FacebookTestUserManager`` module
======================================

Author: Weizhong Yang <zonble at gmail dot com>

A tool which helps to create and delete test account for Facebook.

.. note:: See https://developers.facebook.com/docs/test_users/
'''

class FacebookTestUserManager:
    '''
    The manager which helps to create and delete test accounts.

    >>> appID = '181603781919524'
    >>> appSecret = 'f075c9b716d5b48d04d40275a92c7fc7'
    >>> m = FacebookTestUserManager(appID, appSecret)
    >>> newUser = m.create_test_account('test')
    >>> 'access_token' in newUser
    True
    >>> 'password' in newUser
    True
    >>> 'login_url' in newUser
    True
    >>> 'id' in newUser
    True
    >>> 'email' in newUser
    True
    >>> m.delete_test_user(newUser['id'])
    True
    >>> print m.delete_all_test_users()
    None
    >>> print m.list_test_users()
    []
    '''

    def __init__(self, facebookAppID, facebookSecret):
        '''
        :param facebookAppID: your Facebook App ID.
        :type facebookAppID: str
        :param facebookSecret: your Facebook App Secret.
        :type facebookSecret: str
        '''
        self.app_id = facebookAppID
        self.app_secret = facebookSecret
        self.app_access_token = None

    def _obtain_app_access_token(self):
        GET_parameters = {'client_id': self.app_id,
                          'client_secret': self.app_secret,
                          'grant_type': 'client_credentials'}
        URL = 'https://graph.facebook.com/oauth/access_token?' + \
              urllib.urlencode(GET_parameters)
        response = urllib2.urlopen(URL).read()
        return response[len('access_token='):]

    def create_test_account(self, user_name = 'test_user',
                            permissions=['email', 'publish_stream',
                                         'user_about_me', 'publish_actions']):
        '''
        Create a new test account by giving name and permissions.

        :param user_name: user name of the new account.
        :type user_name: str
        :param permissions: permissions of the new account.
        :type permissions: list
        :returns: a dictionary of the result for regisering a new test
            account.
        :rtype: dict

        '''
        if self.app_access_token == None:
            self.app_access_token = self._obtain_app_access_token()
        GET_parameters = {'installed': 'true',
                          'name': user_name,
                          'locale': 'en_US',
                          'method': 'post',
                          'access_token': self.app_access_token}
        URL = 'https://graph.facebook.com/%s/accounts/test-users?' % self.app_id
        URL += urllib.urlencode(GET_parameters)
        URL += '&permissions=%s' % ','.join(permissions)
        response = urllib2.urlopen(URL).read()
        return json.loads(response)

    def delete_test_user(self, user_id):
        '''
        Delete a test account.

        :param user_id: ID of the user that you want to delete.
        :type user_id: str
        '''
        if self.app_access_token == None:
            self.app_access_token = self._obtain_app_access_token()
        GET_parameters = {'method': 'delete',
                          'access_token': self.app_access_token}
        URL = 'https://graph.facebook.com/%s/?' % user_id
        URL += urllib.urlencode(GET_parameters)
        response = urllib2.urlopen(URL).read()
        return response == 'true'

    def list_test_users(self):
        '''
        List all test accounts.
        '''
        if self.app_access_token == None:
            self.app_access_token = self._obtain_app_access_token()
        URL = 'https://graph.facebook.com/%s/accounts/test-users?' % self.app_id
        URL += 'access_token=' + self.app_access_token
        response = urllib2.urlopen(URL).read()
        return json.loads(response)['data']

    def delete_all_test_users(self):
        '''
        Delete all test users.
        '''
        if self.app_access_token == None:
            self.app_access_token = self._obtain_app_access_token()
        users = self.list_test_users()
        if len(users):
            for user in users:
                self.delete_test_user(user['id'])

if __name__ == "__main__":
    # Call ``python FacebookTestAccount.py -v`` to run doctest.
    import doctest
    doctest.testmod()
