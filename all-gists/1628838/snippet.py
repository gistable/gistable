# Feel free to use me. I'm public domain!
from django.conf import settings
from django import template


register = template.Library()


class OnlySomethingNode(template.Node):
    def __init__(self, nodelist, value='LIVE'):
        self.nodelist = nodelist
        self.value = value

    def render(self, context):
        if getattr(settings, 'DEPLOY_ENVIRONMENT', 'DEV') == self.value:
            return self.nodelist.render(context)

        return ''


@register.tag
def onlylive(parser, token):
    nodelist = parser.parse(('endonlylive',))
    parser.delete_first_token()
    return OnlySomethingNode(nodelist, 'LIVE')


@register.tag
def onlydev(parser, token):
    nodelist = parser.parse(('endonlydev',))
    parser.delete_first_token()
    return OnlySomethingNode(nodelist, 'DEV')