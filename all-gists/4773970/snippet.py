# -*- coding: utf-8 -*-
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import newrelic.agent
newrelic.agent.initialize(os.path.join(os.path.dirname(os.path.dirname(__file__), 'newrelic.ini')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()