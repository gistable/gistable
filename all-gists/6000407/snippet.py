import django
import os

DJANGO_ROOT = os.path.dirname(os.path.realpath(django.__file__))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

'''
Example usage:

STATIC_ROOT = os.path.join(SITE_ROOT, 'static'),

...

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates'),
)
'''