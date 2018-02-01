import functools


def log(func):
    @functools.wraps(func)
    def wrapper(*args):
        print(u"request body: {}".format(args[0]))
        response = func(*args)
        print u"response body: {}".format(response)
        return response

    return wrapper


def append_params(func):
    @functools.wraps(func)
    def wrapper(*args):
        response = func(u"[{}]".format(args[0]))
        return u"={}=".format(response)

    return wrapper


class RequestManager:

    def __init__(self):
        pass

    interceptors = []

    def add_interceptor(self, interceptor):
        self.interceptors.append(interceptor)

    def request(self, body):
        final_request = RequestManager.__real_request
        for interceptor in self.interceptors:
            final_request = interceptor(final_request)
        final_request(body)

    @staticmethod
    def __real_request(body):
        print u"------- real call -------"
        return u"{}'s response".format(body)


manager = RequestManager()
manager.add_interceptor(RequestManager.request)
manager.add_interceptor(log)
manager.request(u"Hello")
