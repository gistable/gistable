import sys
from StringIO import StringIO

class SilencedError ( Exception ):
    pass


class Silencer( object ):
    '''
    suppress stdout and stderr
    
    stdout and stderr are redirected into StringIOs.  At exit their contents are dumped into the string fields 'out' and 'error'
    
    Typically use this via the with statement:
    
    For example::
        
        with Silencer() as fred:
            print stuff
        result = fred.out
        
    note that if you use a silencer to close down output from the logging module, you should call logging.shutdown() in the silencer with block
    '''

    def __init__( self, enabled=True ):
        self.oldstdout = sys.stdout
        self.oldstderr = sys.stderr
        self._outhandle = None
        self._errhandle = None
        self.out = ""
        self.err = ""
        self.enabled = enabled

    def __enter__ ( self ):
        if self.enabled:
            self.oldstdout = sys.stdout
            self.oldstderr = sys.stderr
            sys.stdout = self._outhandle = StringIO()
            sys.stderr = self._errhandle = StringIO()
            self._was_entered = True
            return self
        else:
            self._was_entered = False

    def _restore( self ):
        if self._was_entered:
            self.out = self._outhandle.getvalue()
            self.err = self._errhandle.getvalue()
            sys.stdout = self.oldstdout
            sys.stderr = self.oldstderr
            self._outhandle.close()
            self._errhandle.close()
            self._outhandle = self._errhandle = None

    def __exit__( self, type, value, tb ):
        se = None
        try:
            if type:
                se = SilencedError( type, value, tb )
        except:
            pass
        finally:
            self._restore()
            if se: raise se




