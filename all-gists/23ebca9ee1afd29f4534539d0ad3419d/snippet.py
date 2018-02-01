# Here is an example of some syntax I'm proposing:
# See the github repo at https://github.com/mikeckennedy/python-switch

def test_switch():
    num = 7
    val = input("Enter a key. a, b, c or any other: ")

    with Switch(val) as s:
        s.case('a', process_a)
        s.case('b', process_b)
        s.case('c', lambda: process_with_data(val, num, 'other values still'))
        s.default(process_any)


# process_a, process_b, and process_any are simple void/void methods
def process_a():
    print("Found A!")


def process_b():
    print("Found B!")


def process_any():
    print("Found Default!")
    
def process_with_data(*value):
    print("Found with data: {}".format(value))


# Here is a first pass implementation at adding switch
class Switch:
    def __init__(self, value):
        self.value = value
        self.cases = {}

    def default(self, func: Callable[[], None]):
        self.case('__default__', func)

    def case(self, key, func: Callable[[], None]):
        if key in self.cases:
            raise ValueError("Duplicate case: {}".format(key))
        if not func:
            raise ValueError("Action for case cannot be None.")

        self.cases[key] = func

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        func = self.cases.get(self.value)
        if not func:
            func = self.cases.get('__default__')

        if not func:
            raise Exception("Value does not match any case and there is no default case: value {}".format(self.value))

        func()
