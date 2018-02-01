'''
    Registers render_streamfield tag to add current page context to all block templates.

    Usage: {% render_streamfield a_streamfield %}
    
    Author: github.com/mgd020
'''

from django import template
from wagtail.wagtailcore.blocks.base import Block


register = template.Library()


@register.simple_tag(takes_context=True)
def render_streamfield(context, value):
    def get_context(self, value):
        return dict(context.flatten(), **{
            'self': value,
            self.TEMPLATE_VAR: value,
        })
    Block.get_context = get_context
    return str(value)
