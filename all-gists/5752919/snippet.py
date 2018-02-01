from django import template
from django.conf import settings
import pystache

# Needed to register a custom template tag
register = template.Library()

# Decorator to register a tag that takes the context
@register.simple_tag(takes_context=True)
# Function which takes the django context class and the template string
def mustache(context, template, locale):

# This can be modified to whatever template directory you want to hold your mustache templates
# Opens the file for reading as a raw string, cannot use django's get_template or render_to_string methods
# Because they attempt to render the context and actually return a class which pystache cannot use
  template = open(settings.TEMPLATE_DIRS[0]+"/"+template, 'r').read()

# To retrieve the context passed and not the class info from django, we convert the context to a list
# After converted to a list, if the context is being passed from base, we want the first item in the list
# If the context is passed from a block, we want the second item in the list, from an include the third
  
# In each template load in the custom tag: {% load mustache %}  
  context_map = {
      'base': list(context)[0], # {% mustache "_came_from_base_template.html" 'base' %}
      'block': list(context)[1], # {% mustache "_came_from_block.html" 'include' %}
      'include': list(context)[2] # {% mustache "_came_from_include.html" 'include' %}
  }

# Return the rendered template with pystache
  return  pystache.render(template, context_map[locale])