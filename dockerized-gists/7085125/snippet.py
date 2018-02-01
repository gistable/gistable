class TypeCheck(object):
    def __init__(self,*args):
        self.flags = args
    def __call__(self, original_func):
        decorator_self = self
        def check( *args, **kwargs):
            if len(decorator_self.flags) != len(args):
                raise TypeError("Incorrect number of arguments")
            types = zip(decorator_self.flags,args)
            for (t,a) in types:
                if type(a) != t:
                    raise TypeError("Argument with value " + str(a) + " is not " + str(t))
            return original_func(*args,**kwargs)
        return check

class ReturnCheck(object):
    def __init__(self,*args):
        self.return_type = args[0]
    def __call__(self, original_func):
        decorator_self = self
        def check( *args, **kwargs):
            return_value = original_func(*args,**kwargs)
            if type(return_value) != self.return_type:
                raise TypeError("Return type should be " +str(self.return_type) + " but was " + str(type(return_value)) + " instead.")
            return return_value
        return check



@TypeCheck(int,int)
@ReturnCheck(str)
def myFunction(n,m):
    return str(n + m)

print myFunction(4,6)
