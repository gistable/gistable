"""
resolved_pattern Django context processor: insert the current url's ResolverMatch object into context.

Example use: Set class=active to a menu item, based on the namespace of the currently matched url.

<li {% if resolved.namespace == "home" %}class="active"{% endif %}> home </li>

or more specifically:

<li {% if resolved.view_name == "contact" %}class="active"{% endif %}> contact </li>

See http://docs.djangoproject.com/en/dev/topics/http/urls/#django.conf.urls.defaults.ResolverMatch

"""

from django.core.urlresolvers import resolve

def resolvermatch(request):
    """Add the name of the currently resolved pattern to the RequestContext"""
    match = resolve(request.path)
    if match:
        return {'resolved': match}
    else:
        return {}
