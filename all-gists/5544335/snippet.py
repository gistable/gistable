import uuid

from django import template
from django.template.base import Token, TOKEN_BLOCK

register = template.Library()


class MapNode(template.Node):
    def __init__(self, var_name, tag, list):
        self.var_name = var_name
        self.tag = tag
        self.list = template.Variable(list)

    def render(self, context):
        res = []

        context.push()
        for i in self.list.resolve(context):
            context[self.var_name] = i
            res.append(self.tag.render(context))
        context.pop()

        return ''.join(res)


@register.tag
def map(parser, token):
    _, tag_name, list = token.split_contents()

    var_name = uuid.uuid4().hex
    fake_token = Token(TOKEN_BLOCK, '%s %s' % (tag_name, var_name))
    tag = parser.tags[tag_name](parser, fake_token)
    return MapNode(var_name, tag, list)


# {% map include list_of_templates %}
# {# is like ... #}
# {% for template in list_of_templates %}
#   {% include template %}
# {% endfor %}
