"""Development settings and globals."""


from common import *
from os.path import join, normpath


########## DEBUG CONFIGURATION
DEBUG = True
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
########## END EMAIL CONFIGURATION


########## DATABASE CONFIGURATION
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': normpath(join(SITE_ROOT, 'db', 'default.db')),
		'USER': '',
		'PASSWORD': '',
		'HOST': '',
		'PORT': '',
	}
}
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
	}
}
########## END CACHE CONFIGURATION


########## DJANGO-DEBUG-TOOLBAR CONFIGURATION
MIDDLEWARE_CLASSES += (
	'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += (
	'debug_toolbar',
)

# IPs allowed to see django-debug-toolbar output.
INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_CONFIG = {
	# If set to True (default), the debug toolbar will show an intermediate
	# page upon redirect so you can view any debug information prior to
	# redirecting. This page will provide a link to the redirect destination
	# you can follow when ready. If set to False, redirects will proceed as
	# normal.
	'INTERCEPT_REDIRECTS': False,

	# If not set or set to None, the debug_toolbar middleware will use its
	# built-in show_toolbar method for determining whether the toolbar should
	# show or not. The default checks are that DEBUG must be set to True and
	# the IP of the request must be in INTERNAL_IPS. You can provide your own
	# method for displaying the toolbar which contains your custom logic. This
	# method should return True or False.
	'SHOW_TOOLBAR_CALLBACK': None,

	# An array of custom signals that might be in your project, defined as the
	# python path to the signal.
	'EXTRA_SIGNALS': [],

	# If set to True (the default) then code in Django itself won't be shown in
	# SQL stacktraces.
	'HIDE_DJANGO_SQL': True,

	# If set to True (the default) then a template's context will be included
	# with it in the Template debug panel. Turning this off is useful when you
	# have large template contexts, or you have template contexts with lazy
	# datastructures that you don't want to be evaluated.
	'SHOW_TEMPLATE_CONTEXT': True,

	# If set, this will be the tag to which debug_toolbar will attach the debug
	# toolbar. Defaults to 'body'.
	'TAG': 'body',
}
########## END DJANGO-DEBUG-TOOLBAR CONFIGURATION


########## CELERY CONFIGURATION
INSTALLED_APPS += (
	'djkombu',
)

BROKER_BACKEND = 'djkombu.transport.DatabaseTransport'
########## END CELERY CONFIGURATION