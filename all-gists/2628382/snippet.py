from zope.interface.registry  import Components
from zope.interface import Interface
from zope.interface import Attribute
from zope.interface import provider
from zope.interface import implementer

## global registry
_global_registry = None
def global_registry():
    return _global_registry or Components()

class IView(Interface):
    def __call__(request):
        pass

class IRenderer(Interface):
    def __call__(system, value):
        pass

class IRequest(Interface):
    registry = Attribute("registry")

class IResponse(Interface):
    request = Attribute("request")
    body = Attribute("body")

@provider(IView)
def simple_view(request):
    return {"author": "foo-boo"}

@provider(IRenderer)
def StringRenderer(system, value):
    import StringIO
    io = StringIO.StringIO()
    io.write("----------------------------------------\n")
    for k,v in value.iteritems():
        io.write("\t%s: %s\n" % (k,v))
    return io.getvalue()

@implementer(IResponse)
class Response(object):
    def __init__(self, request, body):
        self.request = request
        self.body = body

    def __str__(self):
        return self.body

class Configurator(object):
    def __init__(self, registry=None):
        self.registry = registry or global_registry()

    def add_view(self, name=None, view=None, renderer=None):
        self.registry.registerUtility(view, IView, name)
        self.registry.registerUtility(renderer, IRenderer, str(view))

class LookUp(object):
    def __init__(self, registry):
        self.registry = registry

    def make_request(self, args, kwargs):
        registry = self.registry
        request = registry.queryUtility(IRequest) or Request()
        request.args = args
        request.kwargs = kwargs
        request.registry = registry
        request.lookup = self
        return request

    def get_view(self, name):
        registry = self.registry
        return registry.getUtility(IView, name)

    def get_renderer(self, view):
        registry = self.registry
        return registry.getUtility(IRenderer, str(view))

class Router(object):
    def __init__(self, config):
        self.config = config
        self.lookup = LookUp(config.registry)

    def __call__(self, name, args=None, kwargs=None):
        request = self.lookup.make_request(args or (), kwargs or {})

        view = self.lookup.get_view(name)
        renderer = self.lookup.get_renderer(view)

        system = dict(config=self.config,
                      route=self,
                      lookup=self.lookup,
                      view_name=name,
                      view=view,
                      request=request)

        value = renderer(system, view(request))
        return Response(request, value)

@implementer(IRequest)
class Request(object):
    pass

if __name__ == "__main__":
    import unittest
    class ReturnValueTest(unittest.TestCase):
        def test_router(self):
            config = Configurator()
            config.add_view("simple", simple_view, StringRenderer)

            router = Router(config)
            result = router("simple")
            expected = u"""\
----------------------------------------
	author: foo-boo
"""
            self.assertEquals(expected, result.body)

        def test_view(self):
            result = simple_view(None)
            self.assertEquals({"author": "foo-boo"}, result)

    unittest.main()
