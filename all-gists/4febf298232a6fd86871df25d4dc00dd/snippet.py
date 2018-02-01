"""
twisted async/await with asyncio reactor and uvloop
"""

import asyncio
import uvloop
from asyncio.tasks import ensure_future

try:
    # as per github source the asyncio reactor is intended to be released in future version
    # https://github.com/twisted/twisted/blob/trunk/src/twisted/internet/asyncioreactor.py
    from twisted.internet import asyncioreactor
except:
    # but for now we can use the reactor in txtulip library
    import txtulip.reactor as asyncioreactor


loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)
asyncioreactor.install(eventloop=loop)

from twisted.web import server
from twisted.web.resource import Resource
from twisted.internet import reactor, endpoints, defer


@defer.inlineCallbacks
def get2(request, resource):
    resource.number_of_requests += 1
    a = yield "Hello world (number:{0}, IP:{1}, session:{2})".format(resource.number_of_requests,
                                                                     request.getClientIP(),
                                                                     request.getSession().uid.decode()).encode()
    return a

async def get(request, resource):
    # please notice that we are awaiting a twisted deferred
    content = await get2(request, resource)
    # of course if an exception occur in get2 which is an inlineCallback, "a" will be a Failure instance
    # the try except will not help here to catch the exception in differed, an instance check will be appropriate
    # eg:
    # if isinstance(a, Failure):
    #     # do some thing set the appropriate http status, log, etc ...

    # note the asyncio sleep will work here
    await asyncio.sleep(0)
    request.setHeader(b"content-length", len(content))
    request.write(content)
    request.finish()


class HelloWorldResource(Resource):
    isLeaf = True
    number_of_requests = 0

    def render_GET(self, request):
        request.setHeader(b"content-type", b"text/plain")
        async_func = get(request, self)
        # defer a python async function
        # replace ensureDeferred (that also work here) by it's asyncio counterpart ensure_future
        # defer.ensureDeferred(async_func)
        ensure_future(async_func)
        return server.NOT_DONE_YET

endpoints.serverFromString(reactor, "tcp:8080").listen(server.Site(HelloWorldResource()))
reactor.run()
