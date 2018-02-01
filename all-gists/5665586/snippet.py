from contextlib import contextmanager

@contextmanager
def module(module_contents):
    def expose(obj):
        module_contents.append(obj.__name__)
        return obj
    yield expose

#Example:
#
#test_module.py:
#
#from expose import module
#__all__ = [] #nessesary to instantiate __all__
#with module(__all__) as expose:
#    @expose
#    def func1():
#        return "Hello"
#
#    @expose
#    def func2():
#        return "World"
#
#    #no expose
#    def func3():
#        return "Goodbye"
#
#
#main1.py:
#
#from test_module import *
#
#print func1() #prints "Hello"
#print func2() #prints "Goodbye"
#print func3() #NameError
#
#
#main2.py
#
##normal imports still work, thanks to Python's thrice-cursed scope leaking.
#impot test_module
#
#print test_module.func1() #prints "Hello"
#print test_module.func2() #prints "World"
#print test_module.func3() #prints "Goodbye"
