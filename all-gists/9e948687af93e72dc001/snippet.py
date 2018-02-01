# Python (Django) snippet to update querystrings. Can be used to:
#   · Replace a value from a querystring key
#   · Append a value to a querystring key
#   · Remove a value from a querystring key
#   · Remove all values from a querystring key
#
# Assuming:
#   Python version: 3.x (tested on 3.4)
#   Django version: 1.8
#   App name: app
#   Directory: project_root/app/templatetags/app_extras.py
#
# Remember to {% load app_extras %} in your HTML template


from urllib.parse import urlencode

from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def update_querystring(context, append=False, **kwargs):
    """
    Updates a querystring according to given `kwargs`. By default, any
    existing key in the querystring will have its value replaced by the
    new value in `kwargs`. Then again, one can set `append` to True; when
    `append` is True, existing keys won't have their values replaced,
    but will have multiple values instead. Good for filtering options.

    From /?foo=bar,
        {% update_querystring foo='baz' %} => /?foo=baz
        {% update_querystring foo='baz' append=True %} => /?foo=bar&foo=baz
    """
    query = dict(context['request'].GET.copy())

    for k, v in kwargs.items():
        v = str(v)
        if k in query and append:
            if v not in query[k]:
                query[k].append(v)
        else:
            query[k] = [v]

    querystring = [(k, i) for k, v in query.items() for i in v]

    return urlencode(querystring)


@register.simple_tag(takes_context=True)
def remove_from_querystring(context, *args, **kwargs):
    """
    Removes a specific value of a key, or all values of a key. One
    specific value will be removed when it's specified in `kwargs`; all
    values of a key will be removed when the key is specified in `args`.

    From /?foo=bar&foo=baz&bar=baz,
        {% remove_from_querystring foo='baz' %} => /?foo=bar&bar=baz
        {% remove_from_querystring 'foo' %} => /?bar=baz
    """

    query = dict(context['request'].GET.copy())

    for item in args:
        if item in query:
            query[item].clear()

    for k, v in kwargs.items():
        v = str(v)
        if k in query and v in query[k]:
            query[k].remove(v)

    querystring = [(k, i) for k, v in query.items() for i in v]

    return urlencode(querystring)
