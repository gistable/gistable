import json
import re

from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, QueryDict
from django.views.decorators.csrf import csrf_exempt

from oauthlib.oauth2.draft25 import AuthorizationEndpoint, TokenEndpoint, ResourceEndpoint
from oauthlib.oauth2.draft25.grant_types import RequestValidator, AuthorizationCodeGrant
from oauthlib.oauth2.draft25.tokens import BearerToken


class TestRequestValidator(RequestValidator):

    def validate_client_id(self, client_id, *args, **kwargs):
        return True

    def validate_client(self, client_id, grant_type, client, *args, **kwargs):
        return True

    def validate_code(self, client_id, code, client, *args, **kwargs):
        return True

    def validate_bearer_token(self, token):
        return True

    def validate_refresh_token(self, refresh_token, client, *args, **kwargs):
        return True

    def authenticate_client(self, request, *args, **kwargs):
        return True

    def validate_scopes(self, client_id, scopes):
        return True

    def confirm_scopes(self, refresh_token, scopes):
        return True

    def validate_user(self, username, password, client=None):
        return True

    def validate_redirect_uri(self, client_id, redirect_uri):
        return True

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client):
        return True

    def get_default_redirect_uri(self, client_id):
        return None


class TestAuthorizationCodeGrant(AuthorizationCodeGrant):

    def save_authorization_code(self, client_id, grant):
        pass

class TestBearerToken(BearerToken):

    def save_token(self, request, token):
        pass


authorization_code_grant = TestAuthorizationCodeGrant(TestRequestValidator())

authorization_endpoint = AuthorizationEndpoint('code',
                            response_types={'code': authorization_code_grant})

default_token = TestBearerToken(TestRequestValidator())

token_endpoint = TokenEndpoint('authorization_code_grant', default_token,
                               {'authorization_code_grant': authorization_code_grant})

resource_endpoint = ResourceEndpoint('Bearer', {'Bearer': default_token})


def get_headers(request):
    regex = re.compile('^HTTP_')
    return dict((regex.sub('', header), value) for (header, value)
                       in request.META.items() if header.startswith('HTTP_'))


def authenticate(request):
    headers = get_headers(request)
    uri = '%s?%s' % (request.path, request.GET.urlencode())
    response_data = authorization_endpoint.create_authorization_response(uri,
                request.method, request.body, headers)

    response = HttpResponseRedirect(response_data[0])
    return response


@csrf_exempt
def token(request):
    headers = get_headers(request)
    uri = '%s?%s' % (request.path, request.GET.urlencode())

    response_data = token_endpoint.create_token_response(uri,
                request.method, request.body, headers)

    response = HttpResponse(response_data[2], status=response_data[3])
    return response


def api(request, *args, **kwargs):
    headers = get_headers(request)
    uri = '%s?%s' % (request.path, request.GET.urlencode())
    if not resource_endpoint.verify_request(uri, request.method, request.body, headers):
        return HttpResponseForbidden('Invalid access_token')
    return HttpResponse(json.dumps(dict(id=1,
                                        name="Someone",
                                        friends=["Somebody", "Nobody"])))