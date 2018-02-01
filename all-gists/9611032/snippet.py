from functools import partial
class MockTask(object):
    def __init__(self, func):
        self.func = func
        
    def delay(self, *args, **kwargs):
        return MockResult(partial(self.func, *args, **kwargs))
        
class MockTask(object):
    def __init__(self, func):
        self.func = func
    def get(self):
        return self.func()
        
def task(func=None, **useless_options):
    if func is None:
        return task
    else:
        return MockTask(func)