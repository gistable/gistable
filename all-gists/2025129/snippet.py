import re

from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()

CONTROL_CHARACTERS = re.compile(r'([\x00-\x1f\x7f-\x9f])*')


@register.filter
@stringfilter
def strip_control_characters(value):
    """Strips Unicode control characters from input."""
    return CONTROL_CHARACTERS.sub('', value)