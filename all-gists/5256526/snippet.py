#!/usr/bin/python

# The urlparse module provides functions for breaking URLs down into their 
# component parts, as defined by the relevant RFCs.

from urlparse import urlparse

# PARSING

parsed = urlparse('http://user:pass@NetLoc:80/path;parameters?query=argument#fragment')
print 'scheme  :', parsed.scheme
print 'netloc  :', parsed.netloc
print 'path    :', parsed.path
print 'params  :', parsed.params
print 'query   :', parsed.query
print 'fragment:', parsed.fragment
print 'username:', parsed.username
print 'password:', parsed.password
print 'hostname:', parsed.hostname, '(netloc in lower case)'
print 'port    :', parsed.port


# To simply strip the fragment identifier from a URL, as you might need to do 
# to find a base page name from a URL, use urldefrag().
from urlparse import urldefrag
original = 'http://netloc/path;parameters?query=argument#fragment'
url, fragment = urldefrag(original)
print url
print fragment

# Result:
# http://netloc/path;parameters?query=argument
# fragment


# UNPARSING
original = 'http://netloc/path;parameters?query=argument#fragment'
parsed = urlparse(original)
print 'UNPARSED:', parsed.geturl()

# If you have a regular tuple of values, you can use urlunparse() to combine them into a URL.
# note that if the input URL included superfluous parts, those may be dropped from the unparsed version of the URL.
original = 'http://netloc/path;parameters?query=argument#fragment'
parsed = urlparse(original)
print 'NEW   :', urlunparse(t)



# JOINING
# In addition to parsing URLs, urlparse includes urljoin() for constructing absolute URLs from relative fragments.
from urlparse import urljoin
print urljoin('http://www.example.com/path/file.html', 'anotherfile.html')
print urljoin('http://www.example.com/path/file.html', '../anotherfile.html')

# Result:
# http://www.example.com/path/anotherfile.html
# http://www.example.com/anotherfile.html

