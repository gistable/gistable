import urllib, hashlib
from django import template
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage

# To use this template tag:
# 1. Add it to the templatetags/ directory of your Django app.
# 2. Then load and use it in the template like so:
#
# {% load gravatar %}
# {% gravatar_url 'foo@bar.com' 96 %}
#
# 3. Configure settings.py:
#
# GRAVATAR_DEFAULT = 'mm'  # Mystery Man.
# GRAVATAR_RATING = 'pg'   # PG rated only.
# GRAVATAR_SIZE = 40       # Size to use if not specified.

register = template.Library()

@register.tag
def gravatar_url(parser, token):
    try:
        token_parts = token.split_contents()
        args = token_parts[1:]
    except ValueError, IndexError:
        raise template.TemplateSyntaxError, "%r tag requires at least one argument" % token.contents.split()[0]
    return GravatarUrlNode(*args)


class GravatarUrlNode(template.Node):
    def __init__(self, email, size=None):
        self.email = template.Variable(email)
        self.size = size

    def render(self, context):
        try:
            email = self.email.resolve(context)
            request = context.get('request')
        except template.VariableDoesNotExist:
            return ''
        except KeyError:
            raise Exception('gravatar_url requires `RequestContext` or `request` in template context')
        # http://en.gravatar.com/site/implement/images/
        params = dict(
            s = self.size or getattr(settings, 'GRAVATAR_SIZE', 40),
            r = getattr(settings, 'GRAVATAR_RATING', 'pg'),
        )
        default = getattr(settings, 'GRAVATAR_DEFAULT', None)
        if default:
            if default not in ('404', 'mm', 'identicon', 'monsterid', 'wavatar', 'retro', ):
                default = staticfiles_storage.url(default)
            params['d'] = default
        proto = 'http'
        host = 'www.gravatar.com'
        if request.is_secure():
            proto += 's'
            host = 'secure.gravatar.com'
        gravatar_url = proto + "://" + host + "/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode(params)
        return gravatar_url