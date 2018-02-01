class CookieMixin(object):
    """
    A CBV mixin that adds an `add_cookie` method on the view, allowing the user
    to set cookies on the response without having direct access to the response
    object itself.

    Example usage::

        class SomeFormView(CookieMixin, FormView):
            ...

            def form_valid(self, form):
                self.add_cookie('form_was_sent', True, max_age=3600)
                return super(SomeFormView, self).form_valid(form)

    """
    def __init__(self, *args, **kwargs):
        super(CookieMixin, self).__init__(*args, **kwargs)
        self._cookies = []

    def get_cookies(self):
        """
        Return an iterable of (args, kwargs) to be passed to set_cookie.
        """
        return self._cookies

    def add_cookie(self, *args, **kwargs):
        """
        Al given arguments will be passed to response.set_cookie later on.
        """
        self.cookies.append((args, kwargs))

    def dispatch(self, request, *args, **kwargs):
        """
        Get the response object from the parent class and sets the cookies on
        it accordingly.
        """
        response = super(CookieMixin, self).dispatch(request, *args, **kwargs)
        for cookie_args, cookie_kwargs in self.get_cookies():
            response.set_cookie(*cookie_args, **cookie_kwargs)
        return response