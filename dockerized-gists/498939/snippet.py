class IllegalDecoratorArgument(Exception):
    pass

class IllegalPassedType(Exception):
    pass

def check_arg(*fargs):
    def decorator(target):
        def wrapper(*args, **kwargs):
            if len(fargs) != len(args):
                raise IllegalDecoratorArgument("Argument does not match the decorator")
            cnt=0
            for t in args:
                if not type(args[cnt]) is eval(fargs[cnt]):
                    raise IllegalPassedType("arg: " + str(args[cnt]) +
                                            " should be of type '" + 
                                            str(fargs[cnt]) + "'")
                cnt+=1
            return target(*args, **kwargs)
        return wrapper
    return decorator

if __name__ == '__main__':
    @check_arg("int", "int")
    def target(a, b):
        return a+b

    target(1, 2)
    target(1, "a")
