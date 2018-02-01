# -*- coding: utf-8 -*-


class SimpleOption(object):

    NOTHING = False
    SOME = True

    def __init__(self, is_some, value=None):

        if is_some:
            self.status = self.SOME
            self.value = value
        else:
            self.status = self.NOTHING

    @property
    def some(self):
        if self.status:
            return self.value
        else:
            return self

    def __ne__(self, other):
        if self.status:
            return self != other
        else:
            return False

    def __eq__(self, other):
        if self.status:
            return self == other
        else:
            return False

    def __call__(self):
        return self.status

    def __getattr__(self, name):
        if name == 'value':
            raise Exception('Direct Get Value Error')
        super(SimpleOption, self).__getattr__(name)

    def __str__(self):
        return "<Option: %s>" % (
            ("Some(" + str(self.some) + ")") if self.status else "Nothing" )

    @classmethod
    def _Nothing(self):
        return SimpleOption(False)

    @classmethod
    def _SOME(self, x):
        return SimpleOption(True, x)

Some = SimpleOption._SOME
Nothing = SimpleOption._Nothing


def _some_wrapper(x):
    if isinstance(x, SimpleOption):
        return x
    return Some(x)


def optional(func):
    def _optional(*args, **kwargs):
        result = func(*args, **kwargs)
        return Nothing() if result is None else result
    return _optional


@optional
def test_recurrence(x, y):
    x = _some_wrapper(x)

    if y <= 0:
        return x

    if x():
        if x.some - y < 0:
            return Nothing()
        else:
            return test_recurrence(
                Some(x.some - 1), y - 1)


@optional
def test_plus_one(x):
    x = _some_wrapper(x)
    if x():
        return Some(x.some + 1)


def double_recurrence(x, y):
    return test_recurrence(
        test_recurrence(x, y), y)

if __name__ == '__main__':
    print test_recurrence(Nothing(), 3)
    print test_recurrence(3, 0)
    print test_recurrence(3, 5)
    print double_recurrence(9, 3)
    print double_recurrence(9, 6)
    print test_plus_one(
        test_recurrence(3, 2))
    print test_plus_one(
        test_recurrence(3, 5))
