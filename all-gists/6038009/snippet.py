DATA = [
    {'number': 2, 'name': 'b'},
    {'number': 1, 'name': 'a'},
    {'number': 4, 'name': 'd'},
]


class Picker(object):
    def __init__(self, lst, key_func=lambda v: v):
        self.lst = lst
        self.key_func = key_func

    def __getitem__(self, match):
        for value in self.lst:
            key = self.key_func(value)
            if key == match:
                return value


def main():
    """
    >>> main()
    1, a
    2, b
    3, None
    4, d
    5, None
    """
    picker = Picker(DATA, lambda v: v['number'])
    for i in range(1, 6):
        value = picker[i]
        print("{}, {}".format(i, value and value['name']))


if __name__ == '__main__':
    main()
