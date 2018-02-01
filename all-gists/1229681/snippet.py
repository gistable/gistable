from django.core.exceptions import MiddlewareNotUsed
from django.conf import settings
import cProfile
import pstats
import marshal
from cStringIO import StringIO

class ProfileMiddleware(object):
    def __init__(self):
        if not settings.DEBUG:
            raise MiddlewareNotUsed()
        self.profiler = None

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.DEBUG and ('profile' in request.GET
                            or 'profilebin' in request.GET):
            self.profiler = cProfile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)

    def process_response(self, request, response):
        if settings.DEBUG:
            if 'profile' in request.GET:
                self.profiler.create_stats()
                out = StringIO()
                stats = pstats.Stats(self.profiler, stream=out)
                # Values for stats.sort_stats():
                # - calls           call count
                # - cumulative      cumulative time
                # - file            file name
                # - module          file name
                # - pcalls          primitive call count
                # - line            line number
                # - name            function name
                # - nfl                     name/file/line
                # - stdname         standard name
                # - time            internal time
                stats.sort_stats('time').print_stats(.2)
                response.content = out.getvalue()
                response['Content-type'] = 'text/plain'
            if 'profilebin' in request.GET:
                self.profiler.create_stats()
                response.content = marshal.dumps(self.profiler.stats)
                filename = request.path.strip('/').replace('/','_') + '.pstat'
                response['Content-Disposition'] = \
                    'attachment; filename=%s' % (filename,)
                response['Content-type'] = 'application/octet-stream'
        return response