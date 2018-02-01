from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# Tells the admin to discover any 'admin.py' files in your apps. Not necessary in Django 1.7+
admin.autodiscover()

urlpatterns = patterns('',
   url(r'^{}/admin/'.format(settings.ADMIN_URL_PATH), include(admin.site.urls)),
   ...
)