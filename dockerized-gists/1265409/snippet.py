import cookielib
import urllib
import urllib2


class Client(object):
    def __init__(self):
        self.cookie_jar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cookie_jar))

        urllib2.install_opener(self.opener)

    def get(self, url, headers={}):
        """HTTP GET

        url should be a string containing a valid URL.
        headers should be a dictionary
        """
        request = urllib2.Request(url, headers=headers)
        return self.execute_request(request)

    def post(self, url, data=None, headers={}):
        """HTTP POST

        url should be a string containing a valid URL.
        data should be a url-encodable dictionary
        headers should be a dictionary
        """
        if data is None:
            postdata = None
        else:
            postdata = urllib.urlencode(data)
        request = urllib2.Request(url, postdata, headers)
        return self.execute_request(request)

    def execute_request(self, request):
        response = self.opener.open(request)
        response.status_code = response.getcode()
        response.data = response.read()
        return response