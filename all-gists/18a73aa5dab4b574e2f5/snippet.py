###################################################
#
#   Usage: 
#       {% load help_text_as_placeholder %}
#       form.field|help_text_as_placeholder
#       OR
#       field|help_text_as_placeholder
###################################################

from django import template
from django.utils.safestring import mark_safe
register = template.Library()

IGNORE_FIELDS = ['<textarea', '<select']


@register.filter("help_text_as_placeholder")
def help_text_as_placeholder(field):
    html = field.as_widget()

    return _get_field_with_placeholder(field, html)


def _get_field_with_placeholder(field, html):
    for ignored_field in IGNORE_FIELDS:
        if (ignored_field not in html):
            html_parts = html.split("/>")
            placeholder = field.help_text or field.name.title()
            html_parts.append('placeholder="{}"'.format(placeholder))
            html_parts.append(' />')
        else:
            return html
    return mark_safe(''.join(html_parts))
