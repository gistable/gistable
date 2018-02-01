from django.conf.urls import include, patterns, url as django_url
import re

def url(pattern, view, kwargs=None, name=None, prefix='', constraints={}):
  '''
  url('/path/:id/to/:something/', some_view, constraints={'id': r'\d{4}'})
  '''
    
    def convert(match):
        name = match.group(1)
        default = r'\d+' if name.endswith('id') else r'\w+'
        return r"(?P<%s>%s)%s" %(name, constraints.get(name, default), match.group(2) or '')
    
    url_pattern = re.sub(r':([a-z\_]+)(/)?', convert, pattern)
    return django_url(url_pattern, view, kwargs, name, prefix)
