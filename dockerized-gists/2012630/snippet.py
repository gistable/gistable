#!/usr/bin/env python2.7

import time

_URL = 'http://localhost/tmp/derp.html'
_NUMBER = 1000


def test_urllib2():
    import urllib2
    try:
        response = urllib2.urlopen(_URL)
    except urllib2.HTTPError, e:
        response = e
    response.code
    return response.read()


def test_urllib3():
    import urllib3
    http = urllib3.PoolManager()
    response = http.request('GET', _URL)
    response.status
    return response.data


def test_requests():
    import requests
    response = requests.get(_URL)
    response.status_code
    return response.text


if __name__ == '__main__':
    from timeit import Timer
    t_urllib2 = Timer("test_urllib2()", "from __main__ import test_urllib2")
    print '{0} urllib2: {1}'.format(_NUMBER,  t_urllib2.timeit(number=_NUMBER))
    t_urllib3 = Timer("test_urllib3()", "from __main__ import test_urllib3")
    print '{0} urllib3: {1}'.format(_NUMBER,  t_urllib3.timeit(number=_NUMBER))
    t_requests = Timer("test_requests()", "from __main__ import test_requests")
    print '{0} requests: {1}'.format(_NUMBER,  t_requests.timeit(number=_NUMBER))

