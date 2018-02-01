import builtins

def testable(f):
    def run_test(test):
        print(test.__doc__)
        args = {name: value for (name, value) in test.__annotations__.items()
                            if name != 'return'}
        assert f(**args) == test.__annotations__['return']
        return test
    f.test = run_test
    return f

@testable
def sum(iterable, start=0):
    return builtins.sum(iterable, start)
    
@sum.test
def test_list(iterable: [1, 2, 3]) -> 6:
    "The sum of a list should work"

@sum.test
def test_gen(iterable: range(5)) -> 10:
    "Ranges are just iterables"
    
@sum.test
def test_failure(iterable: range(1000)) -> 505050:
    "This should fail"