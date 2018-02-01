class TastypieApiKeyUserMiddleware(object):
    """
    Middleware for per-request authentication with tastypie
    """
    # Name of request header to grab username from.  This will be the key as
    # used in the request.META dictionary, i.e. the normalization of headers to
    # all uppercase and the addition of "HTTP_" prefix apply.
    header = 'HTTP_AUTHORIZATION'
    method = 'apikey'
    apikey_auth = ApiKeyAuthentication()


    def process_request(self, request):
        if self.header not in request.META or not request.META[self.header].lower().startswith(self.method + ' '):
            # Let other middleware handle it
            print 'not HTTP_AUTH'
            return

        print 'is HTTP_AUTH'

        auth_type, data = request.META[self.header].split()
        if auth_type.lower() != self.method:

            # Let other middleware handle it
            return

        print 'is apikey'

        # Now, we know it is ApiKey, any unexpected situation 
        # should cause the user to be logout
        
        username, api_key = data.split(':', 1)
        if not username or not api_key:
            auth.logout(request)
            return

        try:
            user = User.objects.get(username=username)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            auth.logout(request)
            return

        try:
            ApiKey.objects.get(user=user, key=api_key)
        except ApiKey.DoesNotExist:
            auth.logout(request)
            return

        if not user.is_active:
            auth.logout(request)
            return

        # If the user is already authenticated we want to verify the user
        if request.user.is_authenticated():
            if request.user == user:
                return

        # Clean username if they mismatch
        if not request.user.is_anonymous():
            self.clean_username(request.user.username, request)
            auth.logout(request)
            return

        request.user = user
        

    def clean_username(self, username, request):
        """
        Allows the backend to clean the username, if the backend defines a
        clean_username method.
        """
        if auth.BACKEND_SESSION_KEY in request.session:
            backend_str = request.session[auth.BACKEND_SESSION_KEY]
            backend = auth.load_backend(backend_str)
            try:
                username = backend.clean_username(username)
            except AttributeError: # Backend has no clean_username method.
                pass
            return username


