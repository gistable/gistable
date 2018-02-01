"""
Using Jinja2 with Django 1.2
Based on: http://djangosnippets.org/snippets/2063/

To use:
  * Add this template loader to settings: `TEMPLATE_LOADERS`
  * Add template dirs to settings: `JINJA2_TEMPLATE_DIRS`

If in template debug mode - we fire the template rendered signal, which allows
debugging the context with the debug toolbar.  Viewing source currently doesnt
work.

If you want {% url %} or {% csrf_token %} support I recommend grabbing them
from Coffin (http://github.com/dcramer/coffin/blob/master/coffin/template/defaulttags.py)
Note for namespaced urls you have to use quotes eg:
  {% url account:login %} => {% url "account:login" %}
"""
import jinja2

from django.template.loader import BaseLoader
from django.template import TemplateDoesNotExist, Origin
from django.core import urlresolvers
from django.conf import settings


class Template(jinja2.Template):
    def render(self, context):
        # flatten the Django Context into a single dictionary.
        context_dict = {}
        for d in context.dicts:
            context_dict.update(d)
        
        if settings.TEMPLATE_DEBUG:
            from django.test import signals
            self.origin = Origin(self.filename)
            signals.template_rendered.send(sender=self, template=self, context=context)
        
        return super(Template, self).render(context_dict)


class Loader(BaseLoader):
    """
    A file system loader for Jinja2.
    
    Requires the following setting `JINJA2_TEMPLATE_DIRS`
    """
    is_usable = True
    
    # Set up the jinja env and load any extensions you may have
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(settings.JINJA2_TEMPLATE_DIRS),
        extensions=(
            'django_jinja2.extensions.URLExtension',
            'django_jinja2.extensions.CsrfExtension',
        )
    )
    env.template_class = Template
    
    # These are available to all templates.
    env.globals['url_for'] = urlresolvers.reverse
    env.globals['MEDIA_URL'] = settings.MEDIA_URL
    
    def load_template(self, template_name, template_dirs=None):
        try:
            template = self.env.get_template(template_name)
            return template, template.filename
        except jinja2.TemplateNotFound:
            raise TemplateDoesNotExist(template_name)