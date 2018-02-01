from os import chdir, getcwd
from os.path import realpath

class PushdContext:
    cwd = None
    original_dir = None

    def __init__(self, dirname):
        self.cwd = realpath(dirname)

    def __enter__(self):
        self.original_dir = getcwd()
        chdir(self.cwd)
        return self

    def __exit__(self, type, value, tb):
        chdir(self.original_dir)

def pushd(dirname):
    return PushdContext(dirname)

# Example use
with pushd('./anfplaylists') as ctx:
    print(ctx.cwd, ctx.original_dir)
print(getcwd())
