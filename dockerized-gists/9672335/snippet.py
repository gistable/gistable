import time
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput


class CallgraphMiddleware(object):
    def process_view(self, request, callback, callback_args, callback_kwargs):

        if settings.DEBUG and 'graph' in request.GET:
            pycallgraph = PyCallGraph(output=GraphvizOutput(output_file='callgraph-' + str(time.time()) + '.png'))
            pycallgraph.start()
            self.pycallgraph = pycallgraph

    def process_response(self, request, response):
        if settings.DEBUG and 'graph' in request.GET:
            self.pycallgraph.done()
        return response