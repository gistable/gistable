# http://stackoverflow.com/questions/748324/python-convert-those-tinyurl-bit-ly-tinyurl-ow-ly-to-full-urls

#############

# urllib2
import urllib2
fp = urllib2.urlopen('http://bit.ly/rgCbf')
fp.geturl()

# ==> 'http://webdesignledger.com/freebies/the-best-social-media-icons-all-in-one-place'

#############

# httplib
import httplib
conn = httplib.HTTPConnection('bit.ly')
conn.request('HEAD', '/rgCbf')
response = conn.getresponse()
response.getheader('location')
# ==> 'http://webdesignledger.com/freebies/the-best-social-media-icons-all-in-one-place'

#############

# pycurl
import pycurl
conn = pycurl.Curl()
conn.setopt(pycurl.URL, "http://bit.ly/rgCbf")
conn.setopt(pycurl.FOLLOWLOCATION, 1)
conn.setopt(pycurl.CUSTOMREQUEST, 'HEAD')
conn.setopt(pycurl.NOBODY, True)
conn.perform()
conn.getinfo(pycurl.EFFECTIVE_URL)
# ==> 'http://webdesignledger.com/freebies/the-best-social-media-icons-all-in-one-place'