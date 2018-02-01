#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Upload a document of any type to Google Docs from the command line. Requires a Google Apps Premier domain and the Google Data APIs Python client (http://code.google.com/p/gdata-python-client/downloads/list).

Usage:

$ pump_to_gdocs.py -f <file name> -t <mime type>

For example, take a database dump and send directly to Google docs:

$ echo 'SELECT * FROM emp;' | mysql -u scott -ptiger scott | pump_to_gdocs.py -f employees -t text/tab-separated-values

See http://code.google.com/apis/documents/overview.html for more info.
"""

import getopt, sys

import gdata.docs.data
import gdata.docs.client

from StringIO import StringIO

from gdata.data import MediaSource
from gdata.gauth import ClientLoginToken

# Login token generated using ClientLogin (see http://code.google.com/apis/accounts/docs/AuthForInstalledApps.html)
# Generate your own using: http://gist.github.com/465526
auth_token = """YOUR_AUTH_TOKEN"""

def pump_to_gdocs(file, file_name=None, content_type=None, content_length=None):
    global auth_token
    
    # Construct client
    client = gdata.docs.client.DocsClient(source='NM-pump_to_gdocs-v1')
    client.ssl = True  # Force all API requests through HTTPS
    client.http_client.debug = False  # Set to True for debugging HTTP requests
    client.auth_token = ClientLoginToken(auth_token)
    
    # Upload the file, and return the created entry
    # See: http://code.google.com/apis/documents/docs/3.0/developers_guide_python.html#UploadingDocContents
    ms = MediaSource(file_handle=file, content_type=content_type, content_length=content_length, file_name=file_name)
    return client.Upload(ms, file_name)
    
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:t:", ["filename=", "type="])
        if len(opts) != 2:
            raise Exception
        opts = dict(opts)
    except Exception:
        print "Usage: pump_to_gdocs.py -f <file name> -t <mime type>"
        sys.exit(2)
    
    file_name = opts.has_key('-f') and opts['-f'] or opts['--filename']
    content_type = opts.has_key('-t') and opts['-t'] or opts['--type']
    
    try:
        data = sys.stdin.read()
    except KeyboardInterrupt, e:
        sys.exit(0)
    
    entry = pump_to_gdocs(StringIO(data), file_name=file_name, content_type=content_type, content_length=len(data))
    
    print entry.GetAlternateLink().href