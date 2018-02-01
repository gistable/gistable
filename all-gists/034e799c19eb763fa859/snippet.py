# From http://vanderwijk.info/blog/adding-css-classes-formfields-in-django-templates/#comment-1193609278

from django import template
register = template.Library()

@register.filter(name='add_attributes')
def add_attributes(field, css):
    attrs = {}
    definition = css.split(',')

    for d in definition:
        if ':' not in d:
            attrs['class'] = d
        else:
            t, v = d.split(':')
            attrs[t] = v

    return field.as_widget(attrs=attrs)