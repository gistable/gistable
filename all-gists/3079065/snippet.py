import os
import barrel

REALM = "PRIVATE"
USERS = [('jacob', 'hunter2')]

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
from django.core.wsgi import get_wsgi_application

application = barrel.cooper.basicauth(users=USERS, realm=REALM)(get_wsgi_application())