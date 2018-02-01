from django import template

register = template.Library()

class UpdateQuerystringNode(template.Node):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def render(self, context):
        query_dict = context['request'].GET.copy()
        for k,v in self.kwargs.items():
            query_dict[k] = v
        return query_dict.urlencode()

@register.tag
def update_querystring(parser, token):
    """
    From /?foo=bar, {% update_querystring foo=baz %}
    will output foo=baz.
    """
    bits = token.split_contents()
    return UpdateQuerystringNode(**dict([bit.split('=') for bit in bits[1:]]))
