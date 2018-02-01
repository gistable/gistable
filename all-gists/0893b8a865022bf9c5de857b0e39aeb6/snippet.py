# author: @Daniel_Abeles
# date:   23/12/2017


def inject_generic_repr(cls):
    """ Injects a generic repr function """
    def generic_repr(that):
        class_items = [f'{k}={v}' for k, v in that.__dict__.items()]
        return f'<{that.__class__.__name__} ' + ', '.join(class_items) + '>'

    cls.__repr__ = generic_repr
    return cls


@inject_generic_repr
class SomeClass(object):
    """ Some Class Example """
    def __init__(self, x, y, z=30):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        """ A lousy repr function """
        return '...'


def main():
    """ Main Function """
    x = SomeClass(10, 20)
    print(x)


if __name__ == '__main__':
    main()

'''
$ python generic_repr.py
<SomeClass x=10, y=20, z=30> 
'''