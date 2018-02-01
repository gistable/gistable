# Two-phased template rendering.
# See http://www.holovaty.com/writing/django-two-phased-rendering/
# LICENSE: Public domain.

################
# TEMPLATE TAG #
################

from django import template
register = template.Library()

def raw(parser, token):
    # Whatever is between {% raw %} and {% endraw %} will be preserved as
    # raw, unrendered template code.
    text = []
    parse_until = 'endraw'
    tag_mapping = {
        template.TOKEN_TEXT: ('', ''),
        template.TOKEN_VAR: ('{{', '}}'),
        template.TOKEN_BLOCK: ('{%', '%}'),
        template.TOKEN_COMMENT: ('{#', '#}'),
    }
    # By the time this template tag is called, the template system has already
    # lexed the template into tokens. Here, we loop over the tokens until
    # {% endraw %} and parse them to TextNodes. We have to add the start and
    # end bits (e.g. "{{" for variables) because those have already been
    # stripped off in a previous part of the template-parsing process.
    while parser.tokens:
        token = parser.next_token()
        if token.token_type == template.TOKEN_BLOCK and token.contents == parse_until:
            return template.TextNode(u''.join(text))
        start, end = tag_mapping[token.token_type]
        text.append(u'%s%s%s' % (start, token.contents, end))
    parser.unclosed_block_tag(parse_until)
raw = register.tag(raw)

##############
# MIDDLEWARE #
##############

from django.core.cache import cache
from django.template import Template
from django.template.context import RequestContext
import urllib

class CachedTemplateMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        response = None
        if request.method == 'GET' and 'magicflag' not in request.GET:
            cache_key = urllib.quote(request.path)
            response = cache.get(cache_key, None)

        if response is None:
            response = view_func(request, *view_args, **view_kwargs)

        if 'magicflag' not in request.GET and response['content-type'].startswith('text/html'):
            t = Template(response.content)
            response.content = t.render(RequestContext(request))

        return response