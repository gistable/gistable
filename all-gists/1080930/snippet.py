'''
@author: asad k awan
@copyright: asad k awan
@license: Apache

'''
import re

from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models.query import QuerySet
from django.shortcuts import render_to_response
from django.utils.cache import patch_response_headers
from django.contrib.auth import SESSION_KEY as AUTH_SESSION_KEY
from django.utils import simplejson as json
from django.core.serializers.json import DjangoJSONEncoder
from base.utils import getFromCacheWithGrace, setToCacheWithGrace, PySer, getBaseTemplateDict
import logging

def wrapper(klass,
            append_request_method = False, 
            pull_params_to_args = False, 
            method = "do", **kwargs):
    """
    Generates returns a callable view handler from handler object.
    """
    t = (method, append_request_method, pull_params_to_args)
    def func(request, **kw):
        o = klass(request, **kw)
        (method, arm, ppta) = t
        if arm:
            r = request.method
            method = "%s_%s" % (method, r)
            if ppta:
                d = getattr(request, r)
                for (k, v) in d.iterlists():
                    kw[str("q_%s" % k)] = v #unicode keys not allowed.
        f = getattr(o, method, o.do)
        try:
            return f(**kw)
        except TypeError, e:
            if unicode(e).startswith(method+'('):
                logging.warn(unicode(e))
                return HttpResponseBadRequest()
            else:
                raise
    return func

class BaseHandler(object):
    '''
    All request handlers to be derived from this class.
    At the least, override do(**kw) function.
    If a different function name is desired, then 
    set method = xx in the call to wrapper.
    For making different handlers for GET, POST, just 
    set 'append_request_method' in the call to wrapper. This will make
    the wrapper call do_GET, do_POST, or xx_GET, ... (if you provided method name).
    You can force URL re match to be parameters to your handler function
    e.g., def do(self, cust_id, **kw) for re'^/customers/(P?<cust_id>\w+)$
    You can also force GET/POST dict to be parameters e.g., 
    def do_GET(self, q_query_param1, **kw)
    For forcing GET/POST params you must set, in the call to wrapper: 
    append_request_method = True and pull_params_to_args = True 
    The GET/POST param variables will have a 'q_' appended to them. So to get a query
    parameter f you will need to have 'q_f' as an arg of the function.
    In every case, remember to have the **kw args to your handler function.
    '''
    
    safeJsonpCbkPattern = re.compile(r'^\w[\.\w]*\w$')
    contentType = {'json': 'application/json; charset=utf-8',
                   'PY': 'py',
                   'js': 'text/javascript; charset=utf-8',
                   'html': 'text/html; charset=utf-8' }
    _pySer = PySer()

    def __init__(self, request, **kw):
        self.req = request
        self.args = kw
        self.logging = logging
        self.template = None
        self._isAuth = None
        self._person = None
        self._outFmt = kw.get('format', 'html').lower()

    def do(self, **kw):
        return self.badRequestResponse('No Impl')
    
    def errorTemplateResponse(self, httpCode=500):
        template = '%d.html' % httpCode
        resp = render_to_response(template, {"request" : self.req})
        resp.status_code = httpCode
        return resp
    
    def badRequestResponse(self, d, *a, **kw):
        fmt = self._outFmt
        kw['content_type'] = self.contentType[fmt]
        if fmt == 'json':
            d = json.dumps({'err': d}, cls = DjangoJSONEncoder) 
            
        return HttpResponseBadRequest(d, *a, **kw)
    
    def response(self, c, *a, **kw):
        outFmt = self._outFmt
        ctype = self.contentType[self._outFmt]
        if ctype == 'py': return c 
        kw['content_type'] = ctype
        if outFmt == 'json':
            return self._jsonResponse(c, *a, **kw)
        elif self.template:
            self.render(self.template, c, *a, **kw)
        else: return HttpResponse(c, *a, **kw)

    def _jsonResponse(self, data, *a, **kw):
        if isinstance(data, QuerySet): data = self._pySer.serialize(data)
        cbk = self.req.GET.get('callback')
        js = json.dumps(data, cls = DjangoJSONEncoder, separators=(',',':'))
        if cbk is not None: # check if jsonp is requested.
            kw['content_type'] = self.contentType['js']
            if self.safeJsonpCbkPattern.match(cbk):
                content = '%s(%s);' %(cbk, js)
            else: content = '["bad cbk %s, need chars only"]' % cbk 
        else: content = js
        return HttpResponse(content, *a, **kw)
    
    def getReferer(self):
        return self.req.META.get('HTTP_REFERER')

    def setCacheHeaders(self, resp, ttl_sec = 0):
        """
        Set the cache headers appropriately.
        if ttl_sec is zero, it will prevent caching.
        """
        patch_response_headers(resp, ttl_sec)
        if ttl_sec <= 0: resp['Cache-Control'] = 'no-cache'
        
    def isAuth(self):
        ### ! NOT FINISHED YET.
        if self._isAuth is not None: return self._isAuth
        # aim is to try not to load req.user object
        ses = self.req.session
        ret = ses.has_key(AUTH_SESSION_KEY)
        self._isAuth = ret
        return ret
    
    def getFromCacheWithGrace(self, key):
        return getFromCacheWithGrace(key)

    def logDbQuery(self, msg):
        from django.db import connection
        self.logging.info('%s %s', msg, str(connection.queries))

    def setToCacheWithGrace(self, key, value, timeout=86400, graceTime=20):
        setToCacheWithGrace(key, value, timeout, graceTime)
    
    def render(self, template_name, dictionary={}, 
               mimetype=contentType['html'], context_instance=None, **kw):
        dictionary.update(getBaseTemplateDict(self))
        return render_to_response(template_name, dictionary = dictionary, mimetype = mimetype,
                                  context_instance = context_instance, **kw)
    
    def pySer(self, queryset, **kw):
        return self._pySer.serialize(queryset, **kw)

