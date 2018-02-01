"""Middleware that removes additional meaningless backslashes.

This transforms URLs as follows:
  - yourwebsite.com// to yourwebsite.com
  - yourwebsite.com/section/// to yourwebsite.com/section


Ideally, this middleware should be placed before Commonmiddleware to avoid
conflicts with APPEND_SLASH. However, this code already appends final slash
if APPEND_SLASH is set to TRUE trying to reduce one additional redirect.
"""
from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin
from django.utils.encoding import escape_uri_path, iri_to_uri


class RemoveTrailingSlashesMiddleware(MiddlewareMixin):
  """Removes all trailing slashes from URL path."""
  def process_request(self, request):
    """Removes backslashes from path_info.

    Args:
      request: User HTTP request.

    Returns:
      request with changes on the path info (URL).
    """
    if request.path[-2:] == '//':
      new_path = request.path.rstrip('/')
      new_url = '{}{}{}'.format(
          escape_uri_path(new_path),
          '/' if settings.APPEND_SLASH else '',
          (
              ('?' + iri_to_uri(request.META.get('QUERY_STRING', '')))
              if request.META.get('QUERY_STRING', '') else ''
          )
      )
      return HttpResponsePermanentRedirect(new_url)
