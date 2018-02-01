from six import add_metaclass


def print_decorator(func):
    def replacement(*args, **kwargs):
        result = func(*args, **kwargs)
        print('The result of the function is: {}'.format(result))
        return result
    return replacement


class MyMetaclass(type):
    def __new__(cls, name, parents, dct):

        # Change methods
        for method in ['myhamjam', 'myfoobar']:
            dct[method] = print_decorator(dct[method])

        return super(MyMetaclass, cls).__new__(cls, name, parents, dct)


@add_metaclass(MyMetaclass)
class Original(object):

    def myhamjam(self):
        return 20

    def myfoobar(self, bar, extra=0):
        return 10 + bar + extra


if __name__ == '__main__':
    my = Original()
    my.myhamjam()
    my.myfoobar(20)
    my.myfoobar(20, extra=100)
