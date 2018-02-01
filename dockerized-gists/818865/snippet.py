from fabric.api import *

class RunAggregator(object):
    def __init__(self):
        self.commands = []
    def __enter__(self):
        return self.commands.append
    def __exit__(self, exc_type, exc_value, traceback):
        run(' && '.join(self.commands))

def test():
    with RunAggregator() as run:
        run('test1')
        run('test2')
        