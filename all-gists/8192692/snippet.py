import httplib
import urlparse

def unshorten_url(url):

    parsed = urlparse.urlparse(url)

    if parsed.scheme == 'https':
        h = httplib.HTTPSConnection(parsed.netloc)
    else:
        h = httplib.HTTPConnection(parsed.netloc)

    resource = parsed.path
    if parsed.query != "": 
        resource += "?" + parsed.query
    h.request('HEAD', resource )
    response = h.getresponse()
    if response.status/100 == 3 and response.getheader('Location'):
        return unshorten_url(response.getheader('Location')) # changed to process chains of short urls
    else:
        return url 