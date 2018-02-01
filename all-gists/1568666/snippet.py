#encoding:utf-8
import logging
import time
import urllib
import mimetools
from tornado import httpclient
from tornado.httputil import HTTPHeaders
from tornado import escape
from tornado.auth import OAuthMixin,OAuth2Mixin

_CONTENT_TYPES = { '.png': 'image/png', '.gif': 'image/gif', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.jpe': 'image/jpeg' }

def _guess_content_type(ext):
    return _CONTENT_TYPES.get(ext, 'application/octet-stream')

def encode_multipart(kw):
    '''
    Build a multipart/form-data body with generated random boundary.
    '''
    boundary = mimetools.choose_boundary()
    data = []
    for k, v in kw.iteritems():
        data.append('--%s' % boundary)
        if hasattr(v, 'read'):
            ext = ''
            filename = getattr(v, 'name', '')
            n = filename.rfind('.')
            if n != (-1):
                ext = filename[n:].lower()
            content = v.read()
            data.append('Content-Disposition: form-data; name="%s"; filename="hidden"' % k)
            data.append('Content-Type: %s' % _guess_content_type(ext))
            data.append('Content-Length: %d' % len(content))
            data.append('Content-Transfer-Encoding: binary')
            data.append('')
            data.append(content)
        else:
            data.append('Content-Disposition: form-data; name="%s";Content-Type: text/plain\r\n' % k)
            data.append('')
            data.append(v.encode('utf-8') if isinstance(v, unicode) else v)
    data.append('--%s--' % boundary)
    return '\r\n'.join(data), boundary


class OldWeiboMixin(OAuthMixin):
    """Weibo OAuth1.0 authentication (not recommended).

    To authenticate with Weibo, register your application with
    Weibo at http://weibo.com/apps. Then copy your Consumer Key and
    Consumer Secret to the application settings 'weibo_consumer_key' and
    'weibo_consumer_secret'. Use this Mixin on the handler for the URL
    you registered as your application's Callback URL.

    When your application is set up, you can use this Mixin like this
    to authenticate the user with Weibo and get access to their stream:

    class WeiboHandler(tornado.web.RequestHandler,
                         tornado.auth.WeiboMixin):
        @tornado.web.asynchronous
        def get(self):
            if self.get_argument("oauth_token", None):
                self.get_authenticated_user(self.async_callback(self._on_auth))
                return
            self.authorize_redirect()

        def _on_auth(self, user):
            if not user:
                raise tornado.web.HTTPError(500, "Weibo auth failed")
            # Save the user using, e.g., set_secure_cookie()

    The user object returned by get_authenticated_user() includes the
    attributes 'username', 'name', and all of the custom Weibo user
    attributes describe at
    http://apiwiki.weibo.com/Weibo-REST-API-Method%3A-users%C2%A0show
    in addition to 'access_token'. You should save the access token with
    the user; it is required to make requests on behalf of the user later
    with weibo_request().
    """
    _OAUTH_REQUEST_TOKEN_URL = "http://api.t.sina.com.cn/oauth/request_token"
    _OAUTH_ACCESS_TOKEN_URL = "http://api.t.sina.com.cn/oauth/access_token"
    _OAUTH_AUTHORIZE_URL = "http://api.t.sina.com.cn/oauth/authorize"
    _OAUTH_AUTHENTICATE_URL = "http://api.t.sina.com.cn/oauth/authenticate"
    _OAUTH_NO_CALLBACKS = False


    def authenticate_redirect(self, callback_uri=None, extra_params=None):
        """Just like authorize_redirect(), but auto-redirects if authorized.

        This is generally the right interface to use if you are using
        Weibo for single-sign on.
        """
        if callback_uri is None:
            callback_uri = self.settings['weibo_login_url']
        if callback_uri and getattr(self, "_OAUTH_NO_CALLBACKS", False):
            raise Exception("This service does not support oauth_callback")
        http = httpclient.AsyncHTTPClient()
        if getattr(self, "_OAUTH_VERSION", "1.0a") == "1.0a":
            http.fetch(self._oauth_request_token_url(callback_uri=callback_uri,
                extra_params=extra_params),
                self.async_callback(
                    self._on_request_token,
                    self._OAUTH_AUTHORIZE_URL,
                callback_uri))
        else:
            http.fetch(self._oauth_request_token_url(), self.async_callback(
                self._on_request_token, self._OAUTH_AUTHORIZE_URL, callback_uri))

    def weibo_request(self, path, callback, access_token=None,
                           post_args=None, **args):
        """Fetches the given API path, e.g., "/statuses/user_timeline/btaylor"

        The path should not include the format (we automatically append
        ".json" and parse the JSON output).

        If the request is a POST, post_args should be provided. Query
        string arguments should be given as keyword arguments.

        All the Weibo methods are documented at
        http://apiwiki.weibo.com/Weibo-API-Documentation.

        Many methods require an OAuth access token which you can obtain
        through authorize_redirect() and get_authenticated_user(). The
        user returned through that process includes an 'access_token'
        attribute that can be used to make authenticated requests via
        this method. Example usage:

        class MainHandler(tornado.web.RequestHandler,
                          tornado.auth.WeiboMixin):
            @tornado.web.authenticated
            @tornado.web.asynchronous
            def get(self):
                self.weibo_request(
                    "/statuses/update",
                    post_args={"status": "Testing Tornado Web Server"},
                    access_token=user["access_token"],
                    callback=self.async_callback(self._on_post))

            def _on_post(self, new_entry):
                if not new_entry:
                    # Call failed; perhaps missing permission?
                    self.authorize_redirect()
                    return
                self.finish("Posted a message!")

        """
        # Add the OAuth resource request signature if we have credentials
        url = "http://api.t.sina.com.cn/" + path + ".json"
        if access_token:
            all_args = {}
            all_args.update(args)
            all_args.update(post_args or {})
            method = "POST" if post_args is not None else "GET"
            oauth = self._oauth_request_parameters(
                url, access_token, all_args, method=method)
            args.update(oauth)
        if args: url += "?" + urllib.urlencode(args)
        callback = self.async_callback(self._on_weibo_request, callback)
        http = httpclient.AsyncHTTPClient()
        if post_args is not None:
            http.fetch(url, method="POST", body=urllib.urlencode(post_args),
                       callback=callback)
        else:
            http.fetch(url, callback=callback)

    def _on_weibo_request(self, callback, response):
        if response.error:
            logging.warning("Error response %s fetching %s", response.error,
                            response.request.url)
            callback(None)
            return
        callback(escape.json_decode(response.body))

    def _oauth_consumer_token(self):
        self.require_setting("weibo_consumer_key", "Weibo OAuth")
        self.require_setting("weibo_consumer_secret", "Weibo OAuth")
        return dict(
            key=self.settings["weibo_consumer_key"],
            secret=self.settings["weibo_consumer_secret"])

    def _oauth_get_user(self, access_token, callback):
        callback = self.async_callback(self._parse_user_response, callback)
        self.weibo_request(
            "/account/verify_credentials",
            access_token=access_token, callback=callback)

    def _parse_user_response(self, callback, user):
        if user:
            user["username"] = user["screen_name"]
        callback(user)
        
class WeiboMixin(OAuth2Mixin):
    """Weibo OAuth2.o authentication.(recommended)

    When your application is set up, you can use this Mixin like this
    to authenticate the user with Weibo and get access to their stream:

    class WeiboHandler(tornado.web.RequestHandler,WeiboMixin):
    
        @tornado.web.asynchronous
        def get(self):
            if self.get_argument("code", None):
                self.get_authenticated_user(
                  redirect_uri='/weibologin',
                  client_id=self.settings["weibo_consumer_key"],
                  client_secret=self.settings["weibo_consumer_secret"],
                  code=self.get_argument("code"),
                  callback=self.async_callback(
                    self._on_auth))
                return
            self.authorize_redirect(redirect_uri='/weibologin',
                                    client_id=self.settings["weibo_consumer_key"])

        def _on_auth(self, user):
            if not user:
                raise tornado.web.HTTPError(500, "Weibo auth failed")
            # Save the user using, e.g., set_secure_cookie()
    """
    _OAUTH_ACCESS_TOKEN_URL = "https://api.weibo.com/oauth2/access_token"
    _OAUTH_AUTHORIZE_URL = "https://api.weibo.com/oauth2/authorize"
    _OAUTH_NO_CALLBACKS = False

    def get_authenticated_user(self, redirect_uri, client_id, client_secret,
                              code, callback, extra_fields=None):
        """Handles the login for the Weibo user, returning a user object."""
        http = httpclient.AsyncHTTPClient()
        args = {
          "redirect_uri": redirect_uri,
          "code": code,
          "client_id": client_id,
          "client_secret": client_secret,
        }
        
        fields = set(['uid','id', 'name', 'screen_name', 'province',
                      'city', 'location', 'description','url',
                      'profile_image_url','gender'])
        if extra_fields: fields.update(extra_fields)
        http.fetch(self._oauth_request_token_url(**args),
            self.async_callback(self._on_access_token, redirect_uri, client_id,
                                client_secret, callback, fields),
                                method="POST",body=urllib.urlencode(args)
                   )
        
    def _on_access_token(self, redirect_uri, client_id, client_secret,
                      callback, fields, response):
        if response.error:
            logging.warning('Weibo auth error: %s' % str(response))
            callback(None)
            return
        
        args = escape.json_decode(response.body)
        session = {
            "access_token": args["access_token"],
            "expires_in": args["expires_in"],
            "uid":args["uid"]
        }

        self.weibo_request(
            path="users/show",
            callback=self.async_callback(
                self._on_get_user_info, callback, session, fields),
                access_token=session["access_token"],
                uid=session["uid"]
            )

    def _on_get_user_info(self, callback, session, fields, user):
        if user is None:
            callback(None)
            return

        fieldmap = {}
        
        for field in fields:
            fieldmap[field] = user.get(field)

        fieldmap.update({"access_token": session["access_token"], "session_expires": session.get("expires_in")})
        callback(fieldmap)

    def is_expires(self, access_token, expires_in):
        if expires_in and access_token:
            return time.time() > float(expires_in)
        else:
            return True
        
    def weibo_request(self, path, callback, access_token=None, expires_in=None,
                           post_args=None, **args):
        url = "https://api.weibo.com/2/" + path + ".json"
        all_args = {}
        if access_token:
            all_args['access_token'] = access_token
        all_args.update(args)
        all_args.update(post_args or {})
        header = HTTPHeaders({'Authorization': 'OAuth2 %s' % access_token})
        callback = self.async_callback(self._on_weibo_request, callback)
        http = httpclient.AsyncHTTPClient()
        if post_args is not None:
            has_file = False
            for key,value in post_args.iteritems():
                if hasattr(value,"read"):
                    has_file = True
            if has_file:
                post_args,boundary = encode_multipart(post_args)
                header.add('Content-Type', 'multipart/form-data; boundary=%s' %boundary)
                header.add('Content-Length', len(post_args))
                http.fetch(url, method="POST", body=post_args,
                           callback=callback,headers=header)
            else:
                http.fetch(url, method="POST", body=urllib.urlencode(all_args),
                           callback=callback,headers=header)
        else:
            if all_args: url += "?" + urllib.urlencode(all_args)
            http.fetch(url, callback=callback,headers=header)

    def _on_weibo_request(self, callback, response):
        if response.error:
            logging.warning("Error response %s %s fetching %s", response.error,response.body,
                            response.request.url)
            callback(None)
            return
        callback(escape.json_decode(response.body))