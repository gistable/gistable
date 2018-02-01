"""
Capture contents of block into context
--------------------------------------

Use case: variable accessing based on current variable values.

{% capture foo %}{{ foo.value }}-suffix{% endcapture %}
{% if foo in bar %}{% endif %}

Created on Monday, February 2012 by Yuji Tomita
"""
from django import template

register = template.Library()

@register.tag
def capture(parser, token):
    nodelist = parser.parse(('endcapture',))
    parser.delete_first_token()
    varname = token.contents.split()[1]
    return CaptureNode(nodelist, varname)

class CaptureNode(template.Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        context[self.varname] = self.nodelist.render(context)
        return ''