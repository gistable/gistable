#!/usr/bin/env python
import urlparse
import mimetypes
import os
import ConfigParser
import urllib2
import json
import csv
import time

class DatastoreClient:
    def __init__(self, url):
        self.parsed = urlparse.urlparse(url)
        newparsed = list(self.parsed)
        username = self.parsed.username
        self.netloc = self.parsed.netloc
        if username:
            # get rid of username:password@ in netloc
            self.netloc = self.parsed.netloc.split('@')[1]
            newparsed[1] = self.netloc
        self.url = urlparse.urlunparse(newparsed)
        self._setup_authorization(username)

    def _upload(self, dict_iterator):
        start = time.time()
        url = self.url + '/_bulk'

        def send_request(data):
            post_data = "%s%s" % ("\n".join(data), "\n")
            req = urllib2.Request(url, post_data, self._headers)
            return urllib2.urlopen(req)

        data = []
        for count,dict_ in enumerate(dict_iterator):
            data.append(json.dumps({"index": {"_id": count+1}}))
            data.append(json.dumps(dict_))
            if (count % 100) == 0:
                response = send_request(data)
                data[:] = []
                print count, (time.time() - start)#, response.read()
        if data:
            send_request(data)
            print count, (time.time() - start)#, response.read()


    def upload(self, filepath_or_fileobj, filetype=None):
        '''Upload data to webstore table. Additional required arguments is file path
        with data to upload and optional {filetype} giving type of file.
        '''
        fileobj = filepath_or_fileobj
        if isinstance(filepath_or_fileobj, basestring):
            if not filetype:
                filetype = mimetypes.guess_type(filepath_or_fileobj)[0]
            fileobj = open(filepath_or_fileobj)
        if filetype.endswith('csv'):
            self._upload(csv.DictReader(fileobj))
        elif filetype.endswith('json'):
            self._upload(json.load(fileobj))
        else: 
            print 'Unsupported format: %s' % filetype

    def delete(self):
        '''Delete this webstore table.'''
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(self.url)
        if self.authorization:
            request.add_header('Authorization', self.authorization)
        request.get_method = lambda: 'DELETE'
        response = opener.open(request)
        return response.read()

    def _setup_authorization(self, username, password=None):
        '''Get authorization field for authorization header.
        
        If password is None we assume username is in fact API key.
        '''
        if username and password:
            secret = username + ':' + password
            self.authorization = 'Basic ' + secret.encode('base64')
        elif username: # API key
            self.authorization = username
        else:
            self.authorization = self._get_api_key_from_config()
        self._headers = {}
        if self.authorization:
            self._headers['Authorization'] = self.authorization

    def _get_api_key_from_config(self):
        config_path = os.path.join(os.path.expanduser('~'), '.dpmrc')
        if os.path.exists(config_path):
            cfgparser = ConfigParser.SafeConfigParser()
            cfgparser.readfp(open(config_path))
            section = 'index:%s' % self.netloc
            if cfgparser.has_section(section):
                api_key = cfgparser.get(section, 'api_key', '')
                return api_key

class TestItOut:
    def test_url_parse(self):
        url = 'http://abc@localhost:8088/api/data/75328a3a-e566-4993-9115-6e915ed7362c'
        client = DatastoreClient(url)
        assert client.netloc == 'localhost:8088'
        assert client.authorization == 'abc'

    def test_delete(self):
        url = 'http://tester@localhost:8088/api/data/75328a3a-e566-4993-9115-6e915ed7362c'
        client = DatastoreClient(url)
        out = client.delete()
        data = json.loads(out)
        assert data['ok'] == True, data

    def test_upload(self):
        url = 'http://tester@localhost:8088/api/data/75328a3a-e566-4993-9115-6e915ed7362c'
        from StringIO import StringIO
        data = StringIO("""[{"a": 1, "b": 2, "c": 3}]""")
        client = DatastoreClient(url)
        client.upload(data, filetype='json')


## ======================================
## Command line interface

import sys
import inspect
import optparse
def _object_methods(obj):
    methods = inspect.getmembers(obj, inspect.ismethod)
    methods = filter(lambda (name,y): not name.startswith('_'), methods)
    methods = dict(methods)
    return methods

def _main(functions_or_object, option_list=None):
    isobject = inspect.isclass(functions_or_object)
    if isobject:
        _methods = _object_methods(functions_or_object)
    else:
        _methods = _module_functions(functions_or_object)

    usage = '''%prog {action} {table-url} [additional-arguments]

table-url is CKAN resource or webstore table url

Actions:
    '''
    usage += '\n    '.join(
        [ '%s: %s' % (name, m.__doc__ if m.__doc__ else '') for (name,m)
        in sorted(_methods.items()) ])
    parser = optparse.OptionParser(usage, option_list=option_list)
    options, args = parser.parse_args()

    if not len(args) >= 2 or not args[0] in _methods:
        parser.print_help()
        sys.exit(1)

    method = args[0]
    url = args[1]
    optdict = options.__dict__
    if isobject:
        getattr(functions_or_object(url), method)(*args[2:], **optdict)
    else:
        _methods[method](*args[1:], **optdict)

if __name__ == '__main__':
    _main(DatastoreClient)
