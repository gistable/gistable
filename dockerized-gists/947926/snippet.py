#
# usage, convert this work method to a Runnable anonymous class
#
#    @anonymous_class(Runnable, 'run')
#    def work(dummy):
#        print 'hello world'
#
#    work.run()
#
import types

_classdict = {}
def anonymous_class(interface, method_name, *args):
    interface_name = interface.__name__
    nextid = _classdict.get(interface_name, -1)+1
    _classdict[interface_name] = nextid

    pseudo_name = "%s$%d" % (interface_name, nextid)
    Pseudo = type(pseudo_name, (interface,), {}) 
    def wrapper(func):
        p = Pseudo(*args)
        setattr(p, method_name, types.MethodType(func, p)) 
        return p
    return wrapper
