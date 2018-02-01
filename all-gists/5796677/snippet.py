from classytags.arguments import Argument, MultiValueArgument
from classytags.values import StringValue

from cms.templatetags.cms_tags import Placeholder, PlaceholderOptions
from cms.models.placeholdermodel import Placeholder as PlaceholderModel

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


class RenderGetPlaceholder(Placeholder):
    """
    Render the content of a placeholder to a variable. Can be provided
    with the name of the placholder (i.e. "Header" in the case of a normal
    CMS page) or a template variable containing a placeholder (i.e. myentry.content in the
    case of an external app using a placeholder)

    {% get_placeholder ["string"|placeholder_var] as variable_name %}
    
    e.g.
    {% load extra_cms_tags %}
    {% get_placeholder "My Placeholder" as my_placeholder %}

    {% if my_placeholder %}
    <div>
        {{ my_placeholder }}
    </div>
    {% endif %}
    """
    name = "get_placeholder"

    options = PlaceholderOptions(
        Argument('name', resolve=True),
        MultiValueArgument('extra_bits', required=False, resolve=False),
        'as',
        Argument('varname', resolve=False, required=True),
        blocks=[
            ('endplaceholder', 'nodelist'),
        ],
    )

    def render_tag(self, context, name, extra_bits, varname, nodelist=None):
        if isinstance(name, PlaceholderModel):
            content = name.render(context, None)
        else:
            content = super(RenderGetPlaceholder, self).render_tag(context, name, extra_bits, nodelist)
        context[varname] = mark_safe(content)
        return ""

    def get_name(self):
        # Fix some template voodoo causing errors
        if isinstance(self.kwargs['name'].var, StringValue):
            return self.kwargs['name'].var.value.strip('"').strip("'")
        return self.kwargs['name'].var.var

register.tag(RenderGetPlaceholder)
