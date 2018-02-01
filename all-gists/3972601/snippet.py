import logging
import facepy as facebook
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.contrib.auth import logout
from django.contrib.auth.models import User

class FBAuthMiddleware(object):
    def __init__(self):
        app_label, model_name = settings.AUTH_PROFILE_MODULE.split(".")
        self.profile_model = models.get_model(app_label, model_name)

    def get_api_key(self, request):
        username = api_key = None

        if request.META.get('HTTP_AUTHORIZATION') and request.META['HTTP_AUTHORIZATION'].lower().startswith('apikey '):
            (auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()

            if auth_type.lower() != 'apikey':
                raise ValueError("Incorrect authorization header.")

            username, api_key = data.split(':', 1)
        else:
            username = request.GET.get('username') or request.POST.get('username')
            api_key = request.GET.get('api_key') or request.POST.get('api_key')
        return username, api_key

    def has_api_key(self, request):
        username, api_key = self.get_api_key(request)
        return username and api_key

    def is_token_valid(self, request, signed_request):
        ''' Try to find out if the token is valid

        we need an api_key and a valid token
        '''
        if not self.has_api_key(request):
            return False

        if not signed_request.user.oauth_token.has_expired:
            return True
        else:
            return False

    def process_request(self, request):
        oauth_token = None
        if request.path.startswith('/js/') or request.path.startswith('/img/')\
         or request.path.startswith('/css/') or request.path.startswith('/admin/'):
            return 

        signed_request = self._get_fb_user_from_cookie(request.COOKIES)
        if not signed_request:
            return 

        # If the data for API key are passed then we don't need the FB data to be fetched real-time
        if self.is_token_valid(request, signed_request):
            request.user = None # to be set by the api key
            return

        try:
            graph = facebook.GraphAPI(signed_request.user.oauth_token.token)
            me = graph.get("me")
        except facebook.FacepyError, e:
            request.user = None
        else:
            # get or create the user
            request.user = self._get_user_for_facebook_graph(me, signed_request.user)
            request.user.graph = graph
            """
                We shamelessly LIE about who authenticated the user.
                TODO: Create a custom backend, when I have time.
            """
            # log the user in (we want is stateless, thus we only send the signal)
            request.user.backend = "django.contrib.auth.backends.ModelBackend"
            user_logged_in.send(sender=request.user.__class__, request=request, user=request.user)

    def _get_user_for_facebook_graph(self, me, request_user):
        user = None
        try:
            profile = self.profile_model.objects.get(**{
                settings.AUTH_PROFILE_MODULE_FACEBOOK_FIELD: request_user.id
            })
        except self.profile_model.DoesNotExist:
            user = self._create_user_for_facebook_graph(me, request_user)
        else:
            user = profile.user
            
        return user

    def _create_user_for_facebook_graph(self, me, request_user):
        user = User()
        user.first_name = me["name"]
        user.email = me["email"]
        user.username = me["email"]
        user.set_unusable_password()
        try:
            user.save()
        except:
            # it seems we have duplicates
            user = User.objects.get(first_name=me['name'])
        else:
            """
                Profile should be created by a post-save
                signal on User. Hopefully..
            """
            profile = user.get_profile()
            setattr(profile, settings.AUTH_PROFILE_MODULE_FACEBOOK_FIELD, request_user.id)
            setattr(profile, settings.AUTH_PROFILE_MODULE_FACEBOOK_TOKEN_FIELD, request_user.oauth_token.token)
            profile.save()

        return user

    def _get_fb_user_from_cookie(self, cookies):
        cookie = cookies.get("fbsr_" + settings.FACEBOOK_APP_ID, "")
        if not cookie:
            return None
        
        try:
            return facebook.SignedRequest(cookie, settings.FACEBOOK_APP_SECRET, settings.FACEBOOK_APP_ID)
        except:
            return None