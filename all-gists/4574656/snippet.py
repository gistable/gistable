"""
This allows clients to log into your Django Tastypie APIs with Facebook (i.e. 
instead of username/password credentials).  

Django-facebook takes care of the communication with Facebook, and updates or 
registers users in your system with their Facebook data.

Rough outline:
1. Install django-facebook
2. Use or extend django-facebook's FacebookProfileModel for your Django AUTH_PROFILE_MODULE
3. Add FacebookAuthentication as authentication on your API
4. Update clients to send a valid FB OAuth access token in the HTTP Authorization header

References:
https://www.djangoproject.com/ (Django)
http://django-tastypie.readthedocs.org/en/latest/toc.html (Django-Tastypie)
https://github.com/tschellenbach/Django-facebook (Django-Facebook)
https://developers.facebook.com/docs/concepts/login/ (Facebook Login)
"""
from tastypie.authentication import Authentication
from django_facebook.connect import connect_user

import logging
logger = logging.getLogger(__name__)

class FacebookAuthentication(Authentication):  
  def __init__(self):
    super(FacebookAuthentication, self).__init__()

  def is_authenticated(self, request, **kwargs):
    auth_params = request.META.get("HTTP_AUTHORIZATION", '')
    if auth_params:
      parts = auth_params.split()
      if len(parts) == 2:
        if parts[0] == 'OAuth':
          access_token = parts[1]
          try:
            action, user = connect_user(request, access_token=access_token)
            return True
          except Exception, err:
            logger.error('ERROR {0}: {1}'.format(self.__class__.__name__, str(err)))
    return False
