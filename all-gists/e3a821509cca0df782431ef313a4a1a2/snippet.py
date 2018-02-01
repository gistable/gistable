import contextlib
import functools

class Defer(contextlib.ExitStack):
    def __call__(self, *args, **kwargs):
        self.callback(functools.partial(*args, **kwargs))

    def __del__(self):
        self.close()


def main():
    defer = Defer()
    print('enter main')

    defer(print, 'deferred')
    print('exit main')

main()
print('exit prog')