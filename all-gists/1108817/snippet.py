from lxml import objectify

from django import template
from django.template.loader import render_to_string

register = template.Library()


class XMLNode(template.Node):
    def __init__(self, xml):
        self.xml = xml

    def render(self, context):
        output = self.xml.render(context)
        xml = objectify.fromstring(output)
        context['object'] = xml
        return render_to_string('xml/%s.html' % xml.tag, context)


@register.tag('xml')
def do_xml(parser, token):
    """
    Convert template XML to an object which renders a corresponding
    HTML template. Lets you embed components using pseudo markup.

    In the main template you'll have something like:

    {% xml %}
        <tabs>
            <tabs url="http://facebook.com" label="Facebook" />
            <tabs url="http://apple.com" label="Apple" />
        </tabs>
    {% endxml %}

    Which renders the template `xml/tabs.html` where you can:

    <div class="tabs">
        {% for tab in object.tab %}
            <a href="{{ tab.attrib.url }}">{{ tab.attrib.label }}</a>
        {% endfor %}
    </div>
    """
    bits = token.split_contents()
    xml = parser.parse(('endxml',))
    parser.delete_first_token()
    return XMLNode(xml)
