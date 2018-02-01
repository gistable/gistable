class required_parameter(object):
    def __init__(self, paramName):
        self.paramName = paramName

    def __call__(self, function):
        def error(param):
            return HttpResponse('Required parameter %s not provided' % param)

        def wrapped_f(*args):
            if (self.paramName in args[0].REQUEST.keys() and args[0].REQUEST.get(self.paramName)):
                return function(*args)
            else:
                return error(self.paramName)
            
        return wrapped_f