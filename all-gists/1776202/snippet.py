# https://gist.github.com/1776202

from os.path import join
from django.http import HttpResponse
from django.views.static import serve
from django.conf import settings


USE_X_ACCEL_REDIRECT = getattr(settings, 'USE_X_ACCEL_REDIRECT', False)
X_ACCEL_REDIRECT_PREFIX = getattr(settings, 'X_ACCEL_REDIRECT_PREFIX', '')


def serve_media(request, file_path):
    """
    Django view that serves a media file using X_ACCEL_REDIRECT_PREFIX if
    USE_X_ACCEL_REDIRECT is enabled in settings, or django.views.static.serve
    if not (for development and testing).
    """

    if USE_X_ACCEL_REDIRECT:
        response = HttpResponse('')
        response['X-Accel-Redirect'] = join('/', X_ACCEL_REDIRECT_PREFIX, file_path)
        response['Content-Type'] = ''

    else:
        response = serve(request, file_path, settings.MEDIA_ROOT)

    return response
