from django.shortcuts import render

class RestfulView(object):
    allowed_methods = ["GET", "POST"]

    def __call__(self, request, *args, **kwargs):
        if request.method not in self.allowed_methods or not hasattr(self, request.method):
            return self.method_not_allowed(request)
        return getattr(self, request.method)(request, *args, **kwargs)

    def method_not_allowed(self, request):
        return render(request, "405.html", status=405)
