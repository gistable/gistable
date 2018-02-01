from pyramid.view import view_config

class ViewDefaults(object):

    def __init__(self, **settings):
        self._default_settings = settings

    def view(self, **view_settings):
        effective_settings = self._default_settings.copy()
        effective_settings.update(view_settings)
        return view_config(**effective_settings)


# create instance, for ex. in package __init__.py
view_defaults = ViewDefaults(renderer='json', xhr=True)

# decorate view
from myapp import view_defaults

# any default setting can be overwritten using this decorator (renderer in this case)
@view_defaults.view(name='example', renderer='template.mako', request_method='GET')
def my_view(context, request):
    return {'foo': 'bar'}

