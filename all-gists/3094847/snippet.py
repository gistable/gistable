from django import template

register = template.Library()

@register.filter(name='indent')
def indent_string(val, num_spaces=4):
    return val.replace('\n', '\n' + ' '*num_spaces)
