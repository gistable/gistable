import unicodedata

from django import template

register = template.Library()


@register.filter
def truncate(text, max_length):
    max_length = int(max_length) - 3
    length = 0
    wide_widths = ['F', 'W', 'A']
    for i in range(len(text)):
        if text[i] == '@' or text[i].isupper():
            length += 2
        elif unicodedata.east_asian_width(text[i]) not in wide_widths:
            length += 1
        else:
            length += 2
        if length == max_length:
            return text[:i + 1] + '...'
        if length > max_length:
            return text[:i] + '...'
    return text
