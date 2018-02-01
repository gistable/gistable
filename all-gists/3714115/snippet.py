"""qurl is a tag to append, remove or replace query string parameters from an url (preserve order)"""
 
import re
from django.template import Library, Node, TemplateSyntaxError
from urlparse import urlparse, parse_qsl, urlunparse
from django.utils.encoding import smart_str
from urllib import urlencode
 
 
register = Library()
 
 
@register.tag
def qurl(parser, token):
    """
    Append, remove or replace query string parameters from an url (preserve order)
 
        {% qurl url [param]* [as <var_name>] %}
 
    param:
            name=value: replace all values of name by one value
            name=None: remove all values of name
            name+=value: append a new value for name
            name-=value: remove the value of name with the value
 
    Example::
 
        {% qurl '/search?page=1&color=blue&color=green' order='name' page=None color+='red' color-='green' %}
        Output: /search?color=blue&order=name&color=red
 
        {% qurl request.get_full_path order='name' %}
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument (url)" % bits[0])
 
    url = parser.compile_filter(bits[1])
 
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]
 
    qs = []
    if len(bits):
        kwarg_re = re.compile(r"(\w+)(\-=|\+=|=)(.*)")
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to url tag")
            name, op, value = match.groups()
            qs.append((name, op, parser.compile_filter(value),))
 
    return QURLNode(url, qs, asvar)
 
 
class QURLNode(Node):
    """Implements the actions of the qurl tag."""
 
    def __init__(self, url, qs, asvar):
        self.url = url
        self.qs = qs
        self.asvar = asvar
 
    def render(self, context):
        urlp = list(urlparse(self.url.resolve(context)))
        qp = parse_qsl(urlp[4])
        for name, op, value in self.qs:
            name = smart_str(name)
            value = value.resolve(context)
            value = smart_str(value) if value is not None else None
            if op == '+=':
                qp = filter(lambda (n, v): not(n == name and v == value), qp)
                qp.append((name, value,))
            elif op == '-=':
                qp = filter(lambda (n, v): not(n == name and v == value), qp)
            elif op == '=':
                qp = filter(lambda (n, v): not(n == name), qp)
                if value is not None:
                    qp.append((name, value,))
 
        urlp[4] = urlencode(qp, True)
        url = urlunparse(urlp)
 
        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url