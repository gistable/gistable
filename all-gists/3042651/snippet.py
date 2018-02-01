"""
Template tags for creating links to media files, which are suffixed with the media file's
mtime (foo.jpg?123456) for the purposes of cache busting.

Use:
- Put this file in a `<django-app>/templatetags/` directory
- To link to media files from a template, use:

    {% load media_link %}
    {% stylesheet_link "css/base.css" %}
    {% script_link "js/base.js %}
    <img src="{% media_url "foo.jpg" %}" />

  Which would yield HTML equivalent to:

    <link rel="stylesheet" href="{{ MEDIA_URL }}css/base.css?123" type="text/css" />
    <script type="text/javascript" src="{{ MEDIA_URL }}js/base.js?456"></script>
    <img src="{{ MEDIA_URL }}foo.jpg?789" />

"""

import os

from django import template
from django.utils.safestring import mark_safe

from django.conf import settings as s

register = template.Library()

def _mtime_suffix(file):
    return int(os.stat(s.MEDIA_ROOT + file).st_mtime)

@register.simple_tag
def media_url(file):
    return "%s%s?%s" %(s.MEDIA_URL, file, _mtime_suffix(file))

@register.simple_tag
def stylesheet_link(stylesheet):
    return mark_safe('<link rel="stylesheet" href="%s%s?%d" type="text/css" />' %(
        s.MEDIA_URL,
        stylesheet,
        _mtime_suffix(stylesheet),
    ))

@register.simple_tag
def script_link(script):
    return mark_safe('<script type="text/javascript" src="%s%s?%d"></script>' %(
        s.MEDIA_URL,
        script,
        _mtime_suffix(script)
    ))
