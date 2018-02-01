# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.inclusion_tag('template.html', takes_context = True)
def tag(context):
    pass
