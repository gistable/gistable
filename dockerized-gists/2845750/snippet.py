#Given to the public domain
#No warranties
import urllib2
import simplejson

def shorturl(urltoshorten):
    """Compress the URL using goo.gl take a look at https://developers.google.com/url-shortener/v1/getting_started
    
    >>> shorturl('http://igor.tamarapatino.org')
    'http://goo.gl/FxHOn'
    """
    try:
        apiurl = "https://www.googleapis.com/urlshortener/v1/url"
        req = urllib2.Request(apiurl,
            headers={'Content-Type': 'application/json'},
            data='{{"longUrl": "{0}"}}'.format(urltoshorten))
        shorturl = simplejson.loads(urllib2.urlopen(req).read())['id']
    except:
        shorturl = urltoshorten
    return shorturl

if __name__ == "__main__":
    import doctest
    doctest.testmod()