from django.views.generic import View
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.views import login


class WrapperView(View):

    @property
    def view_function(self):
        raise ImproperlyConfigured("You must define a 'view_function'.")

    def dispatch(self, *args, **kwargs):
        kwargs.update(self.get_settings())
        return self.view_function.im_func(*args, **kwargs)

    def get_settings(self):
        return {}


class LoginView(WrapperView):
    view_function = login
    template_name = 'accounts/login.html'

    def get_settings(self):
        return {
            'template_name': self.template_name
        }
