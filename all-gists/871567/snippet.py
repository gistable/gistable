"""
Wrapper for loading templates from "templates" directories in INSTALLED_APPS
packages, prefixed by the appname for namespacing.

This loader finds `appname/templates/index.html` when looking for something
of the form `appname/index.html`.
"""

from django.template import TemplateDoesNotExist
from django.template.loaders.app_directories import app_template_dirs, Loader as BaseAppLoader

class Loader(BaseAppLoader):
    '''
    Modified AppDirectory Template Loader that allows namespacing templates
    with the name of their app, without requiring an extra subdirectory
    in the form of `appname/templates/appname`.
    '''
    def load_template_source(self, template_name, template_dirs=None):
        try:
            app_name, template_path = template_name.split('/', 1)
        except ValueError:
            raise TemplateDoesNotExist(template_name)

        if not template_dirs:
            template_dirs = (d for d in app_template_dirs if
                    d.endswith('/%s/templates' % app_name))

        return iter(super(Loader, self).load_template_source(template_path,
                template_dirs))
