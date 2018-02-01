#!/usr/bin/python
# coding=utf-8
from __future__ import print_function
import httplib2
import os
import re
import base64

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    msgs = service.users().messages().list(userId='me', q=u"from:(cht_ebpp@cht.com.tw) subject:(電信費用通知單)").execute()
    if not msgs:
        print("email not found")
    else:
        for msg in msgs['messages']:
            mail = service.users().messages().get(userId='me', id=msg['id']).execute()
            for part in (mail['payload']['parts']):
                filename = None
                data = None
                if part['filename'] and 'data' in part['body']:
                    data=part['body']['data']
                    filename = part['filename']
                elif (part['mimeType'] == 'application/pdf'):
                    att_id = part['body']['attachmentId']
                    filename = re.split("name=", part['headers'][0]['value'])[1]
                    attachment = service.users().messages().attachments().get(userId='me', messageId=msg['id'], id=att_id).execute()
                    data = attachment['data']
                if filename is not None:
                    print("Saving %s file size: %d" % (filename, part['body']['size']))
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                    with open(filename, 'w') as f:
                        f.write(file_data)

if __name__ == '__main__':
    main()
