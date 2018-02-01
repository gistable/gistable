from django.conf import settings
from django.conf.urls.defaults import include, patterns
from django.http import HttpResponse
from django.utils.encoding import smart_unicode

if 'debug_toolbar' not in settings.INSTALLED_APPS:
    class DebugMiddleware(object):
        pass
else:
    import debug_toolbar.urls
    from debug_toolbar.middleware import DebugToolbarMiddleware, replace_insensitive
    from debug_toolbar.toolbar.loader import DebugToolbar

    class DebugMiddleware(DebugToolbarMiddleware):
        def _show_toolbar(self, request):
            if '_debug' not in request.GET:
                return False
            if not self._process_urls(request):
                return False
            return True

        def _process_urls(self, request):
            # Modify this to fit your own internal logic
            if not ((request.user.is_authenticated() and request.user.is_superuser) or settings.DEBUG):
                return False
            if (request.is_ajax() and not debug_toolbar.urls._PREFIX in request.path):
                return False
            return True
        
        def process_request(self, request):
            if self._process_urls(request):

                if self.override_url:
                    original_urlconf = getattr(request, 'urlconf', settings.ROOT_URLCONF)
                    debug_toolbar.urls.urlpatterns += patterns('',
                        ('', include(original_urlconf)),
                    )
                    self.override_url = False
                request.urlconf = 'debug_toolbar.urls'
                toolbar = DebugToolbar(request)

                toolbar.orig_DEBUG = settings.DEBUG
                settings.DEBUG = True

                for panel in toolbar.panels:
                    panel.process_request(request)
                
                self.debug_toolbars[request] = toolbar

        def process_response(self, request, response):
            toolbar = self.debug_toolbars.get(request)
            if not toolbar:
                return response

            settings.DEBUG = toolbar.orig_DEBUG

            if not self._show_toolbar(request):
                return response

            response = HttpResponse('''<html><head></head><body></body><script type="text/javascript">djdt.ready(function(d){
                var $ = d.jQuery;
                d.show_toolbar(false);
                $($("#djDebugPanelList .djDebugPanelButton a")[0]).click();
            });</script></html>''')

            for panel in toolbar.panels:
                panel.process_response(request, response)

            response.content = replace_insensitive(
                smart_unicode(response.content), 
                self.tag,
                smart_unicode(toolbar.render_toolbar() + self.tag))

            if response.get('Content-Length', None):
                response['Content-Length'] = len(response.content)

            del self.debug_toolbars[request]
            return response