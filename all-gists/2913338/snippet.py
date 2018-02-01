from django.utils.decorators import method_decorator

def class_decorator(decorator):
    def inner(cls):
        orig_dispatch = cls.dispatch
        @method_decorator(decorator)
        def new_dispatch(self, request, *args, **kwargs):
            return orig_dispatch(self, request, *args, **kwargs)
        cls.dispatch = new_dispatch
        return cls
    return inner


# usage:
# in views.py
#
#    from django.views.decorators.cache import cache_control
#    from django.views.generic import View
#    @class_decorator(cache_control(max_age=60))
#    class MyView(View):
#        filename = 'templatefile'
#        def content(self, request):
#            ...