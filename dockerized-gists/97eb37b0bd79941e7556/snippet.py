class YoctoAuthApp(object):
    def __init__(self, auth_obj={}):
        _.auth_obj = auth_obj
    def __call__(self, env, start):
        def rstart(resp):
            start(resp, [('Content-Type', 'application/json'),
                         ('Access-Control-Allow-Origin', '*'), ])
        try:
            data = self.auth_obj
            ret  = [ '{}' ]
            pre  = env['PATH_INFO'][:5]
            post = env['PATH_INFO'][5:]
            if   pre=='/add/':
                data[post] = True
            elif pre=='/del/':
                del data[post]
            elif pre=='/get/':
                ret=[ data[post] ]
            else:
                raise Exception( "ERROR" )
            rstart('200 OK')
            return ret
        except:
            rstart('404 Not Found')
            return [ 'null' ]
import json
class JSONPersistentDict(dict):
    def __init__(self, fname):
        self.fname = fname
        self.update( json.load( fname ) )
    def __setitem__(self, *a, **kw):
        json.dump( self, open( self, fname, 'w' ) )
        return super(JSONPersistentDict,self).__setitem__(*a, **kw)
class YoctoJSONPersistentDictAuthApp(JSONPersistentDict, YoctoAuthApp):
    def __init__(self, fname):
        JSONPersistentDict.__init__(self, fname)
        AuthApp.__init__(self, self)