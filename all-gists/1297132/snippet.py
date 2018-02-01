import lldb

class Executioner(object):
    typemap = {
        None:  'void',
        int:   'int',
        float: 'float',
        str:   'char *',
    }
    
    class Function(object):
        def __init__(self, name):
            self.name = name
            self.returns = None

        def __call__(self, *args):
            argStrs = [ ]
            for arg in args:
                if isinstance(arg, str):
                    argStrs.append('"%s"' % arg.replace('\\', '\\\\').replace('"', '\"'))
                else:
                    argStrs.append(repr(arg))
            
            expr = '(%s)%s(%s)' % (Executioner.typemap[self.returns], self.name, ', '.join(argStrs))
            return lldb.frame.EvaluateExpression(expr)
    
    def __init__(self):
        self._funcs = { }
    
    def __getattr__(self, name):
        fn = Executioner.Function(name)
        setattr(self, name, fn)
        return fn

lldb.exec = Executioner()