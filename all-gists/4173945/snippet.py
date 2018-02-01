#!/usr/bin/env python2.6
import base64
import sys
import json
import imaplib
import urllib
from optparse import OptionParser

import atom.http_core

from oauth2client import client

class Error(Exception):
    def __str__(self):
        return "Error: %s" % self.error_message

class OAuth2JWTError(Error):
    """Raised when an OAuth2 error occurs."""
    def __init__(self, error_message):
        self.error_message = error_message


def get_JWT(assertion):
    body = urllib.urlencode({
            'grant_type':'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion':assertion
        }
    ) 
    headers = {}

    http_client = atom.http_core.HttpClient()
    http_request = atom.http_core.HttpRequest(uri="https://accounts.google.com/o/oauth2/token",
            method="POST", headers=headers)
    http_request.add_body_part(data=body, mime_type="application/x-www-form-urlencoded")
    response = http_client.Request(http_request)
    body = response.read()

    if response.status == 200:
        return body
    else:
        error_msg = 'Invalid response %s.' % response.status
        try:
            d = json.loads(body)
            if 'error' in d:
                error_msg = d['error']
        except:
            pass
        raise OAuth2JWTError(error_msg)

def get_service_private_key():
    f = open('service_privatekey.p12','rb')
    key = f.read()
    f.close()
    return key

def get_clientSecrets():
    f = open('service_client_secrets.json')
    secrets_json = f.read()
    return json.loads(secrets_json)

def getServiceAccountsAccessToken(user):
    client_secrets = get_clientSecrets()
    private_key = get_service_private_key()

    scope = "https://mail.google.com/"
    jwt_client = client.SignedJwtAssertionCredentials(
            service_account_name=client_secrets['web']['client_email'],
            private_key=private_key,
            scope=scope,
            prn=user)

    jwt = json.loads(get_JWT(jwt_client._generate_assertion()))
    access_token = jwt["access_token"]
    return access_token

def GenerateOAuth2String(username, access_token, base64_encode=True):
    """Generates an IMAP OAuth2 authentication string.

    See https://developers.google.com/google-apps/gmail/oauth2_overview

    Args:
    username: the username (email address) of the account to authenticate
    access_token: An OAuth2 access token.
    base64_encode: Whether to base64-encode the output.

    Returns:
    The SASL argument for the OAuth2 mechanism.
    """
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (username, access_token)
    if base64_encode:
        auth_string = base64.b64encode(auth_string)
    return auth_string

def getUnreadCountFromIMAP(user, auth_string):
    """Authenticates to IMAP with the given auth_string.

    Prints a debug trace of the attempted IMAP connection.

    Args:
    user: The Gmail username (full email address)
    auth_string: A valid OAuth2 string, as returned by GenerateOAuth2String.
        Must not be base64-encoded, since imaplib does its own base64-encoding.
    """
    print
    imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
    imap_conn.debug = 4
    imap_conn.authenticate('XOAUTH2', lambda x: auth_string)
    imap_conn.select('INBOX', readonly=True)
    typ, data = imap_conn.search(None, "UNSEEN")
    unreads = data[0].split()
    return len(unreads)

def getUnreadCountFromFeed(access_token):
    import urllib2
    from xml.dom import minidom
    GMAIL_FEED_URI="https://mail.google.com/mail/feed/atom"

    request = urllib2.Request(GMAIL_FEED_URI)
    request.add_header("Authorization", "Bearer %s" %  access_token)
    response = urllib2.urlopen(request)
    feed = response.readlines()
    feed_string = "\n".join(feed)

    dom = minidom.parseString(feed_string)
    unread = dom.getElementsByTagName("fullcount")[0].childNodes[0].nodeValue
    return unread

def SetupOptionParser():
    # Usage message is the module's docstring.
    parser = OptionParser(usage=__doc__)
    parser.add_option('--user',
                    default=None,
                    help='email address of user whose account is being '
                         'accessed')
    return parser

def main():
    opt_parser = SetupOptionParser()
    (options, args) = opt_parser.parse_args()
    if options.user is None:
        print("--user Required.")
        sys.exit(-1)
    user = options.user 

    access_token = getServiceAccountsAccessToken(user)
    
    unread_imap = getUnreadCountFromIMAP(user,
        GenerateOAuth2String(user, access_token,
                             base64_encode=False))
    print("%d unread message(s)" % unread_imap)

    unread = getUnreadCountFromFeed(access_token)
    print("%s unread message(s)" % unread)

if __name__ == '__main__':
    main()