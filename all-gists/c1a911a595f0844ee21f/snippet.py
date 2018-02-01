'''
A simple demonstration of obtaining, modifying and executing code objects in python without relying 
on commonly blocked keywords such as exec, compile, etc...

-Patrick Biernat.
'''

import __builtin__

mydict = {}
mydict['__builtins__'] = __builtin__

def f():
        pass

def mkfunc():
        function = type(f)
        code = type(f.__code__)
        bytecode = "7400006401006402008302006a010083000053".decode('hex')
        filename = "./poc.py"
        consts = (None,filename,'r')
        names = ('open','read')
        codeobj = code(0, 0, 3, 64, bytecode, consts, names, (), 'noname', '<module>', 1, '', (), ())
        return function(codeobj, mydict, None, None, None)

g = mkfunc()
print g()
