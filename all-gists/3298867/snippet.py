"""WSGI application file"""

import os
from django.core.wsgi import get_wsgi_application
from barrel import cooper

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

django_app = get_wsgi_application()

auth_decorator = cooper.basicauth(
    users=[('someuser', 'somepass'),], 
    realm='Password Protected'
)

application = auth_decorator(django_app)