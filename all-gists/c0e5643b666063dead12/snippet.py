# Exemplo com closure
def crazy_sum():
    acc = 0

    def wrapped(t):
        nonlocal acc

        sum_with_acc = sum(t) + acc

        acc = max(0, sum_with_acc - 9)
        digit = sum_with_acc % 10

        return digit

    return wrapped

crazy_sum = crazy_sum()

# Exemplo com classe
class Somador:
    acc = 0

    def __call__(self, t):
        sum_with_acc = sum(t) + self.acc

        self.acc = max(0, sum_with_acc - 9)
        digit = sum_with_acc % 10

        return digit


def sum_digits(l1, l2):
    somador = Somador()
    l = [somador(t) for t in zip(l1, l2)]

    if somador.acc:
        l.append(somador.acc)

    return l

# Exemplo com classe e um init boladão
class Somador:
    acc = 0

    def __init__(self, *args):

        self.result = [self(t) for t in zip(*args)]

        if self.acc:
            self.result.append(self.acc)

    def __call__(self, t):
        sum_with_acc = sum(t) + self.acc

        self.acc = max(0, sum_with_acc - 9)
        digit = sum_with_acc % 10

        return digit


def sum_digits(*args):
    return Somador(*args).result

assert list(sum_digits([1, 0], [1, 1])) == [2, 1]
assert list(sum_digits([9, 0], [1, 1])) == [0, 2]
assert list(sum_digits([3, 1, 5], [5, 9, 2])) == [8, 0, 8]
assert list(sum_digits([3, 1, 9], [5, 9, 2])) == [8, 0, 2, 3]
assert list(sum_digits([1, 1], [2, 2], [3, 7])) == [6, 0, 1]


