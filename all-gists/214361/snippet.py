"""
Here's my sample Django settings for a project I recently did. Visit http://damonjablons.wordpress.com to see the explanation.
"""

import os
import socket

# Set DEBUG = True if on the production server
if socket.gethostname() == 'your.domain.com':
    DEBUG = False
else:
    DEBUG = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Damon Jablons', 'damon@fake.email.com'),
)

MANAGERS = ADMINS

# The database settings are left blank so to force the use of local_settings.py below
DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# This dynamically discovers the path to the project
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '%sadmin-media/' % MEDIA_URL

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'OH_NOES!'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

# Context Processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)

if DEBUG:
    TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.debug',)
if USE_I18N:
    TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.i18n',)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

if DEBUG:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = ()
for root, dirs, files in os.walk(PROJECT_PATH):
    if 'templates' in dirs: TEMPLATE_DIRS += (os.path.join(root, 'templates'),)

INSTALLED_APPS = (

    # Django Applications
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',

    # Third Party Django Applications
    'django_extensions',
    'sorl.thumbnail',
    'filebrowser',
    'chunks',
    'registration',
    
    # Project Applications
    'use',
    'wsgi',
    'and',
    'dont',
    'include',
    'the',
    'project',
    'name',
)

if DEBUG:
    INSTALLED_APPS += ('debug_toolbar',)

TEMPLATE_TAGS = (
    'sorl.thumbnail.templatetags.thumbnail',
    'scribblitt.general.templatetags.rotator_includes',
    'chunks.templatetags.chunks',
)

# SORL Settings
THUMBNAIL_EXTENSION = 'png'

# Filebrowser Settings
FILEBROWSER_URL_WWW = os.path.join(MEDIA_URL, 'uploads%s' % os.sep)
FILEBROWSER_PATH_SERVE = os.path.join(MEDIA_ROOT, 'uploads')
FILEBROWSER_URL_FILEBROWSER_MEDIA = os.path.join(MEDIA_URL, 'filebrowser%s' % os.sep)
FILEBROWSER_PATH_FILEBROWSER_MEDIA = os.path.join(MEDIA_ROOT, 'filebrowser')

# Registration App Settings
ACCOUNT_ACTIVATION_DAYS = 3
LOGIN_REDIRECT_URL = '/'

INTERNAL_IPS = (
    '127.0.0.1',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

try:
    from local_settings import *
except ImportError:
    pass