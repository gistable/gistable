# -*- encoding: UTF-8 -*-

import os
import httplib2

# pip install --upgrade google-api-python-client
from oauth2client.file import Storage
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow

# Copy your credentials from the console
# https://console.developers.google.com
CLIENT_ID = 'xxxxxx'
CLIENT_SECRET = 'yyyyyyyy'


OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
OUT_PATH = os.path.join(os.path.dirname(__file__), 'out')
CREDS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')

if not os.path.exist(OUT_PATH):
    os.makedirs(OUT_PATH)

storage = Storage(CREDS_FILE)
credentials = storage.get()

if credentials is None:
    # Run through the OAuth flow and retrieve credentials
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    print 'Go to the following link in your browser: ' + authorize_url
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    storage.put(credentials)


# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)

def list_files(service):
    page_token = None
    while True:
        param = {}
        if page_token:
            param['pageToken'] = page_token
        files = service.files().list(**param).execute()
        for item in files['items']:
            yield item
        page_token = files.get('nextPageToken')
        if not page_token:
            break


for item in list_files(drive_service):
    if item.get('title').upper().startswith('OFFER'):
        outfile = os.path.join(OUT_PATH, '%s.pdf' % item['title'])
        download_url = None
        if 'exportLinks' in item and 'application/pdf' in item['exportLinks']:
            download_url = item['exportLinks']['application/pdf']
        elif 'downloadUrl' in item:
            download_url = item['downloadUrl']
        else:
            print 'ERROR getting %s' % item.get('title')
            print item
            print dir(item)
        if download_url:
            print "downloading %s" % item.get('title')
            resp, content = drive_service._http.request(download_url)
            if resp.status == 200:
                if os.path.isfile(outfile):
                    print "ERROR, %s already exist" % outfile
                else:
                    with open(outfile, 'wb') as f:
                        f.write(content)
                    print "OK"
            else:
                print 'ERROR downloading %s' % item.get('title')




