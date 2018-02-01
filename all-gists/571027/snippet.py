from django.http import HttpRequest

class PickleableHttpRequest(HttpRequest):
    def __init__(self, request=None, attributes=None):
        super(PickleableHttpRequest, self).__init__()

        if request:
            if not isinstance(request, HttpRequest):
                raise Exception('Request supplied is not a valid HTTP request object.')

            self.GET = request.GET
            self.POST = request.POST
            self.REQUEST = request.REQUEST
            # Do not load FILES or META. These structures can't be pickled

        if attributes:
            for attribute in attributes:
                if hasattr(request, attribute):
                    setattr(self, attribute, getattr(request, attribute))