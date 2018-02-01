class BaseRequestHandler(tornado.web.RequestHandler):
    """Base class for all SimpleGeo request handlers."""

    def _handle_request_exception(self, e):
        status_code = getattr(e, 'status_code', 500)
        self.set_status(status_code)

        error = {
            'code' : status_code,
            'message' : str(e)
        }

        _logger.exception(e)
        self.finish(json.dumps(error, indent=4))

    def prepare(self):
        realm = SGSettings.get('web', 'realm')
        header, value = oauth.build_authenticate_header(realm).items()[0]
        self.set_header(header, value)

        try:
            uri = '%s://%s%s' % (self.request.protocol, self.request.host,
                self.request.path)

            # Builder our request object.
            request = oauth.Request.from_request(
                self.request.method, uri, self.request.headers, None,
                self.request.query)
        except Exception, e:
            _logger.info("Could not parse request from method = %s,"
                "uri = %s, headers = %s, query = %s, exception = %s" % (
                self.request.method, uri, self.request.headers,
                self.request.query, e))
            raise NotAuthorized()

        # Fetch the token from Cassandra and build our Consumer object.
        if request is None or 'oauth_consumer_key' not in request:
            _logger.debug("Request is missing oauth_consumer_key.")

            raise NotAuthorized()

        try:
            token = Token(token=request['oauth_consumer_key'])
        except Exception, e:
            _logger.info("Token not found %s (%s, %s)." % (
                request['oauth_consumer_key'], e, request))
            raise NotAuthorized()

        try:
            consumer = oauth.Consumer(key=token.key, secret=token.secret)
        except Exception, e:
            _logger.info("Could not instantiate oauth.Consumer (%s)." % e)
            raise NotAuthorized()

        try:
            # Verify the two-legged request.
            server = oauth.Server()
            server.add_signature_method(oauth.SignatureMethod_HMAC_SHA1())
            server.verify_request(request, consumer, None)
        except Exception, e:
            _logger.info("Could not verify signature (%s)." % e)
            raise NotAuthorized()