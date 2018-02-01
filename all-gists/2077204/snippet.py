import urllib2

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

class HEADRedirectHandler(urllib2.HTTPRedirectHandler):
    """
    Subclass the HTTPRedirectHandler to make it use our 
    HeadRequest also on the redirected URL
    """
    def redirect_request(self, req, fp, code, msg, headers, newurl): 
        if code in (301, 302, 303, 307):
            newurl = newurl.replace(' ', '%20') 
            return HeadRequest(newurl, 
                               headers=req.headers, 
                               origin_req_host=req.get_origin_req_host(), 
                               unverifiable=True) 
        else: 
            raise urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)

# Build our opener with the HEADRedirectHandler
opener = urllib2.OpenerDirector() 
for handler in [urllib2.HTTPHandler, urllib2.HTTPDefaultErrorHandler,
                HEADRedirectHandler,
                urllib2.HTTPErrorProcessor, urllib2.HTTPSHandler]:
    opener.add_handler(handler())

response = opener.open(HeadRequest(url))

print response.geturl()
print response.info()