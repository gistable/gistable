#!/usr/bin/env python

"""
urlnorm.py - URL normalisation routines

urlnorm normalises a URL by;
  * lowercasing the scheme and hostname
  * taking out default port if present (e.g., http://www.foo.com:80/)
  * collapsing the path (./, ../, etc)
  * removing the last character in the hostname if it is '.'
  * unquoting any %-escaped characters

Available functions:
  norms - given a URL (string), returns a normalised URL
  norm - given a URL tuple, returns a normalised tuple
  test - test suite
  
CHANGES:
0.92 - unknown schemes now pass the port through silently
0.91 - general cleanup
     - changed dictionaries to lists where appropriate
     - more fine-grained authority parsing and normalisation    
"""

__license__ = """
Copyright (c) 1999-2002 Mark Nottingham <mnot@pobox.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = "0.93"

from urlparse import urlparse, urlunparse
from urllib import unquote
from string import lower
import re

_collapse = re.compile('([^/]+/\.\./?|/\./|//|/\.$|/\.\.$)')
_server_authority = re.compile('^(?:([^\@]+)\@)?([^\:]+)(?:\:(.+))?$')
_default_port = {   'http': '80',
                    'https': '443',
                    'gopher': '70',
                    'news': '119',
                    'snews': '563',
                    'nntp': '119',
                    'snntp': '563',
                    'ftp': '21',
                    'telnet': '23',
                    'prospero': '191',
                }
_relative_schemes = [   'http',
                        'https',
                        'news',
                        'snews',
                        'nntp',
                        'snntp',
                        'ftp',
                        'file',
                        ''
                    ]
_server_authority_schemes = [   'http',
                                'https',
                                'news',
                                'snews',
                                'ftp',
                            ]


def norms(urlstring):
    """given a string URL, return its normalised form"""
    return urlunparse(norm(urlparse(urlstring)))


def norm(urltuple):
    """given a six-tuple URL, return its normalised form"""
    (scheme, authority, path, parameters, query, fragment) = urltuple
    scheme = lower(scheme)
    if authority:
        userinfo, host, port = _server_authority.match(authority).groups()
        if host[-1] == '.':
            host = host[:-1]
        authority = lower(host)
        if userinfo:
            authority = "%s@%s" % (userinfo, authority)
        if port and port != _default_port.get(scheme, None):
            authority = "%s:%s" % (authority, port)
    if scheme in _relative_schemes:
        last_path = path
        while 1:
            path = _collapse.sub('/', path, 1)
            if last_path == path:
                break
            last_path = path
    path = unquote(path)
    return (scheme, authority, path, parameters, query, fragment)



def test():
    """ test suite; some taken from RFC1808. """
    tests = {    
        '/foo/bar/.':                    '/foo/bar/', 
        '/foo/bar/./':                   '/foo/bar/',
        '/foo/bar/..':                   '/foo/',
        '/foo/bar/../':                  '/foo/',
        '/foo/bar/../baz':               '/foo/baz',
        '/foo/bar/../..':                '/',
        '/foo/bar/../../':               '/',
        '/foo/bar/../../baz':            '/baz',
        '/foo/bar/../../../baz':         '/../baz',
        '/foo/bar/../../../../baz':      '/baz',
        '/./foo':                        '/foo',
        '/../foo':                       '/../foo',
        '/foo.':                         '/foo.',
        '/.foo':                         '/.foo',
        '/foo..':                        '/foo..',
        '/..foo':                        '/..foo',
        '/./../foo':                     '/../foo',
        '/./foo/.':                      '/foo/',
        '/foo/./bar':                    '/foo/bar',
        '/foo/../bar':                   '/bar',
        '/foo//':                        '/foo/',
        '/foo///bar//':                  '/foo/bar/',    
        'http://www.foo.com:80/foo':     'http://www.foo.com/foo',
        'http://www.foo.com:8000/foo':   'http://www.foo.com:8000/foo',
        'http://www.foo.com./foo/bar.html': 'http://www.foo.com/foo/bar.html',
        'http://www.foo.com.:81/foo':    'http://www.foo.com:81/foo',
        'http://www.foo.com/%7ebar':     'http://www.foo.com/~bar',
        'http://www.foo.com/%7Ebar':     'http://www.foo.com/~bar',
        'ftp://user:pass@ftp.foo.net/foo/bar': 'ftp://user:pass@ftp.foo.net/foo/bar',
        'http://USER:pass@www.Example.COM/foo/bar': 'http://USER:pass@www.example.com/foo/bar',
        'http://www.example.com./':      'http://www.example.com/',
        '-':                             '-',
    }

    n_correct, n_fail = 0, 0
    test_keys = tests.keys()
    test_keys.sort()            
    for i in test_keys:
        print 'ORIGINAL:', i
        cleaned = norms(i)
        answer = tests[i]
        print 'CLEANED: ', cleaned
        print 'CORRECT: ', answer
        if cleaned != answer:
            print "*** TEST FAILED"
            n_fail = n_fail + 1
        else:
            n_correct = n_correct + 1
        print        
    print "TOTAL CORRECT:", n_correct
    print "TOTAL FAILURE:", n_fail


if __name__ == '__main__':
    test()
