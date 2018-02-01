""" Django-admin autoregister -- automatic model registration
Original: http://djangosnippets.org/snippets/2066/

## sample admin.py ##

from yourproject.autoregister import autoregister

# register all models defined on each app
autoregister('app1', 'app2', 'app3', ...)

"""

from django.db.models import get_models, get_app
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

def autoregister(*app_list):
    for app_name in app_list:
        app_models = get_app(app_name)
        for model in get_models(app_models):
            try:
                admin.site.register(model)
            except AlreadyRegistered:
                pass