#! /usr/bin/env python
'''
This is more of a personal reference as I use json very often.
The httplib2 examples are VERY good, and you should refer to them:

http://code.google.com/p/httplib2/wiki/Examples
'''

from httplib2 import Http
try:
    # For c speedups
    from simplejson import loads, dumps
except ImportError:
    from json import loads, dumps

# These aren't needed, just for this example
import logging
from pprint import pformat

def post_dict(url, dictionary):
    '''
    Pass the whole dictionary as a json body to the url.
    Make sure to use a new Http object each time for thread safety.
    '''
    http_obj = Http()
    resp, content = http.request(
        uri=url,
        method='POST',
        headers={'Content-Type': 'application/json; charset=UTF-8'},
        body=dumps(dictionary),
    )
    logging.info('Response dictionary")
    logging.info(pformat(resp))
    logging.info("Response Content Body")
    logging.info(pformat(content))

def main():
    # NOTE you would need to setup a webapp that can accept a json post to test this.
    # Perhaps ill show a quick example in a later post

    post_dict(
        url='http://127.0.0.1/services/something_that_accepts_a_json_post',
        dictionary={'test': 'this is only a test'}
    )

if __name__ == "__main__":
    main()