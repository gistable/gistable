import functools
import logging


def test_test1(*dargs, **dkwargs):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(request, *args, **kwargs):
            logging.warning("plouf plouf 1")
            return function(request, *args, **kwargs)
        return wrapper
    return decorator


def test_test2(*dargs, **dkwargs):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(request, *args, **kwargs):
            logging.warning("plouf plouf 2")
            return function(request, *args, **kwargs)
        return wrapper
    return decorator


@test_test2()
@test_test1()
def test(test):
    logging.warning("plouf plouf OK {0}".format(test))



test("toc")



# florian@maximini:~/Desktop$ python ~/Desktop/test.py 
# WARNING:root:plouf plouf 2
# WARNING:root:plouf plouf 1
# WARNING:root:plouf plouf OK toc