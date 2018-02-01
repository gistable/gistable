from pprint import PrettyPrinter
from random import randrange


def post_order(t, deep=0):
    if isinstance(t, dotdict):
        # is a node
        yield deep, t.value
        yield from post_order(t.left, deep+1)
        yield from post_order(t.right, deep+1)
    else:
        # is a leaf
        yield deep, t


def in_order(t, deep=0):
    if isinstance(t, dotdict):
        # is a node
        yield from in_order(t.left, deep+1)
        yield deep, t.value
        yield from in_order(t.right, deep+1)
    else:
        # is a leaf
        yield deep, t


def pre_order(t, deep=0):
    if isinstance(t, dotdict):
        # is a node
        yield from pre_order(t.left, deep+1)
        yield from pre_order(t.right, deep+1)
        yield deep, t.value
    else:
        # is a leaf
        yield deep, t


def main():
    tree = dotdict({
        'value': randrange(100),
        'left': dotdict({
            'value': randrange(100),
            'left': dotdict({
                'value': randrange(100),
                'left': randrange(100),
                'right': randrange(100)
            }),
            'right': randrange(100)
        }),
        'right': dotdict({
            'value': randrange(100),
            'left': randrange(100),
            'right': dotdict({
                'value': randrange(100),
                'left': randrange(100),
                'right': randrange(100)
            }),
        })
    })

    pp = PrettyPrinter(indent=2)
    pp.pprint(tree)

    print('\nIN-ORDER VISIT')
    for deep, item in in_order(tree):
        print('deep:{} value:{}'.format(deep, item))

    print('\nPOST-ORDER VISIT')
    for deep, item in post_order(tree):
        print('deep:{} value:{}'.format(deep, item))

    print('\nPRE-ORDER VISIT')
    for deep, item in pre_order(tree):
        print('deep:{} value:{}'.format(deep, item))


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


if __name__ == '__main__':
    main()
