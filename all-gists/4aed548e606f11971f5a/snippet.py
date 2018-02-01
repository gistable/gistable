from rest_framework import status

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.settings import api_settings
from social.apps.django_app.utils import strategy
from social.backends.oauth import BaseOAuth1, BaseOAuth2

from api.serializers.social_login import ObtainSocialAuthTokenSerializer


@strategy()
def _register_by_access_token(request, backend):
	"""
	Checks what OAuth protocol is being used for social authentication, backend corresponds to the allowed backend types
	and authenticates the user using the access token from the request.
	"""
	backend = request.strategy.backend

	if isinstance(backend, BaseOAuth1):
		token = {
			'oauth_token': request.POST.get('access_token'),
			'oauth_token_secret': '<secret>'  # required by python-social-auth, but is not used
		}
	elif isinstance(backend, BaseOAuth2):
		token = request.POST.get('access_token')
	else:
		raise Response("Wrong backend type", status=status.HTTP_400_BAD_REQUEST)

	return backend.do_auth(token)


class ObtainSocialAuthTokenView(ObtainAuthToken):
	serializer_class = ObtainSocialAuthTokenSerializer
	renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
	parser_classes = api_settings.DEFAULT_PARSER_CLASSES

	class Meta():
		list_wrapper = "tokens"
		instance_wrapper = "token"

	def post(self, request, backend):
		serializer = self.serializer_class(data=request.DATA)

		if serializer.is_valid():
			user = _register_by_access_token(request, backend)
			if user:
				user_url = reverse('user-instance', args=[user.pk], request=request)
				token, created = Token.objects.get_or_create(user=user)
				return Response({'token': token.key, 'user_id': user.id, 'user_url': user_url})

		return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)