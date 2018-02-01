import sys


class Stupid(Exception):
    pass


class X:

    def __getattr__(self, name):
        print("You won't get %s" % name)
        return Stupid


x = X()


def test(err=None):
    try:
        if err:
            raise err
    except ValueError:
        print('what?')
    except x.LazyEval as e:
        print(e)
    except sys.not_exist_at_all:
        pass


if __name__ == '__main__':
    error = sys.argv[1] if len(sys.argv) > 1 else None
    if error == 'value':
        error = ValueError
    elif error == 'type':
        error = Stupid
    elif error == 'other':
        error = OSError
    test(error)
