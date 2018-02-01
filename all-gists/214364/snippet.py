from django.conf import settings
from django.template import add_to_builtins
import django.template.loader

try:
    for lib in settings.TEMPLATE_TAGS:
        add_to_builtins(lib)
except AttributeError:
    pass

from django.utils.translation import ugettext
import __builtin__
__builtin__.__dict__['_'] = ugettext