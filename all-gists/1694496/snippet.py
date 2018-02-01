"""
This allows you to import Django modules into a Salt module
"""

import logging
import sys
import os

log = logging.getLogger(__name__)

# point this at the virtualenv dir that your django deployment runs out of
# you are using virtualenv. right?
DJANGO_ENV = '/home/core/python-envs/production'

# where your code lives (ie where settings.py is)
DJANGO_DIR = '/home/core/code/production'

log.debug("Preparing Django modules...")

# add our site packages
import site
site_packages = os.path.join(DJANGO_ENV, 'lib', 'python%s' % sys.version[:3], 'site-packages')
site.addsitedir(site_packages)

# put the main Django directory on first
sys.path.insert(0, DJANGO_DIR)

# setup the Django environment pointing to our settings
import settings
import django.core.management
django.core.management.setup_environ(settings)

# finally, import our objects
from yourapp.models import YourModel