"""
=============
stringmethods
=============

Make possible to use all Python string methods as Django template filters. Also
provide custom template tag ``{% stringmethod %}`` to use methods with more
than one argument, like ``format``, ``count`` and other.

Restrictions
============

1. Django template system do not provide multiple arguments for filters, so
   for calling::

       'The sum of {0} and {1} is {2}.'.format(1, 2, 3)

   you need to use ``{% stringmethod %}`` template tag. E.g.::

       {% load string_filters %}
       {% stringmethod "The sum of {0} and {1} is {2}." 1 2 3 %}

2. Django template system allow to use only named arguments in filter or
   simple tag definition, and doesn't understand using of magic ``*args`` list.
   For string methods this problem fixes by using max of three arguments, cause
   ``count``, ``endswith``, ``find``, ``index``, ``replace``, ``rfind``,
   ``rindex`` and ``startswith`` works with three arguments, other methods
   needs two args or lower.

3. Keyword arguments for ``format`` method does not supported.

4. ``stringfilters`` does not support ``join`` string method for honor of
   using built-in Django template filter.

Installation
============

Save this gist anywhere of ``templatetags`` directory for app listed in
``INSTALLED_APPS``.

Usage
=====

Django already provides several Python string methods as template filters.
There are ``center``, ``ljust``, ``lower``, ``rjust``, ``title`` and ``upper``.

And ``stringmethods`` allow to use all another string methods in your
Django templates.

Using Python string methods as Django template filters
------------------------------------------------------

This solution is good for particular reasons, but bad for ``replace`` or other
methods needed more that one argument. Example, python code::

    '\tfor i in range(4):\n'.expandtabs(4)
    'http://www.google.com/'.rstrip('/')

In Django templates::

    {{ "\tfor i in range(4)"|expandtabs:4 }}
    {{ "http://www.google.com/"|rstrip:"/" }}

Using {% stringmethod %} template tag
-------------------------------------

For advanced reasons or for ``replace`` method you should use this template
tag. Let's see examples, python code::

    'abc'.replace('abc', 'def')
    '1 2 Some text'.split(' ', 2)

In Django templates::

    {% stringmethod "replace" "abc" "abc" "def" %}
    {% stringmethod "split" "1 2 Some text" " " 2 %}

"""

from django.template import Library
from django.template.defaultfilters import stringfilter


register = Library()

IGNORE_METHODS = ['join']


@register.simple_tag
def stringmethod(name, value, first=None, second=None, third=None):
    return make_filter(name)(value, first, second, third)


@stringfilter
def make_filter(name):
    def filter(value, first=None, second=None, third=None):
        args = [first, second, third]
        method = getattr(value, name)

        while True:
            try:
                return method(*args)
            except TypeError:
                args.pop(len(args) - 1)

    return filter


for name in dir(u''):
    # Ignore all private string methods
    if name.startswith('_'):
        continue

    # Ignore ``join`` method
    if name in IGNORE_METHODS:
        continue

    # Create new template filters for all string methods that not yet added
    # to Django template built-ins
    register.filter(name, make_filter(name))
