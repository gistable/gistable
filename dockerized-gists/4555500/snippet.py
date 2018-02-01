

from tornado import httpclient
from tornado import auth
from tornado import httputil
from tornado import escape
import urllib
#from tornado.httputil import url_concat


class LinkedInMixin(auth.OAuthMixin):
    _OAUTH_REQUEST_TOKEN_URL = "https://api.linkedin.com/uas/oauth/requestToken"
    _OAUTH_ACCESS_TOKEN_URL = "https://api.linkedin.com/uas/oauth/accessToken"
    _OAUTH_AUTHORIZE_URL = "https://www.linkedin.com/uas/oauth/authorize"
    _OAUTH_AUTHENTICATE_URL = "https://www.linkedin.com/uas/oauth/authenticate"
    _OAUTH_VERSION = "1.0"
    _OAUTH_NO_CALLBACKS = False
    #  http://developer.linkedin.com/docs/DOC-1002
    _DEFAULT_USER_FIELDS = "(id,first-name,last-name,headline,industry,positions,educations,summary,picture-url)"

    def authenticate_redirect(self):
        """Just like authorize_redirect(), but auto-redirects if authorized.

        This is generally the right interface to use if you are using
        LinkedIn for single-sign on.
        """
        http = httpclient.AsyncHTTPClient()
        http.fetch(self._oauth_request_token_url(), self.async_callback(
            self._on_request_token, self._OAUTH_AUTHENTICATE_URL, None))

    def linkedin_request(self, path, callback, access_token=None, post_args=None, **args):
        url = "http://api.linkedin.com" + path
        if access_token:
            all_args = {}
            all_args.update(args)
            all_args.update(post_args or {})
            method = "POST" if post_args is not None else "GET"
            oauth = self._oauth_request_parameters(
                url, access_token, all_args, method=method)
            args.update(oauth)
        if args:
            url += "?" + urllib.urlencode(args)
        callback = self.async_callback(self._on_linkedin_request, callback)
        http = httpclient.AsyncHTTPClient()
        # ask linkedin to send us JSON on all API calls (not xml)
        headers = httputil.HTTPHeaders({"x-li-format": "json"})
        if post_args is not None:
            http.fetch(url, method="POST", headers=headers, body=urllib.urlencode(post_args), callback=callback)
        else:
            http.fetch(url, headers=headers, callback=callback)

    def _parse_user_response(self, callback, user):
        callback(user)

    def _on_linkedin_request(self, callback, response):
        if response.error:
            logging.warning("Error response %s fetching %s", response.error, response.request.url)
            callback(None)
        else:
            callback(escape.json_decode(response.body))

    def _oauth_consumer_token(self):
        self.require_setting("linkedin_consumer_key", "LinkedIn OAuth")
        self.require_setting("linkedin_consumer_secret", "LinkedIn OAuth")
        return dict(
            key=self.settings["linkedin_consumer_key"],
            secret=self.settings["linkedin_consumer_secret"])

    def _oauth_get_user(self, access_token, callback):
        callback = self.async_callback(self._parse_user_response, callback)
        self.linkedin_request("/v1/people/~:%s" % self._DEFAULT_USER_FIELDS, access_token=access_token, callback=callback)


class LinkedInLogin(tornado.web.RequestHandler, LinkedInMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("oauth_token", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authorize_redirect(callback_uri=None)

    def _on_auth(self, user):
        print 'return from auth'
        print user
        if not user:
            raise tornado.web.HTTPError(500, "LinkedIn auth failed")
        else:
            print 'we are in'
            # Save the user using, e.g., set_secure_cookie()

