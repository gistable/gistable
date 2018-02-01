from django.contrib.auth.models import User
from tastypie.authentication import ApiKeyAuthentication

class EmailApiKeyAuthentication (ApiKeyAuthentication):
    """ The same as base class, but use email to find user """
    def is_authenticated(self, request, **kwargs):
        email = request.GET.get('username') or request.POST.get('username')
        api_key = request.GET.get('api_key') or request.POST.get('api_key')

        if not email or not api_key:
            return self._unauthorized()

        try:
            user = User.objects.get(email=email)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return self._unauthorized()

        request.user = user
        return self.get_key(user, api_key)
