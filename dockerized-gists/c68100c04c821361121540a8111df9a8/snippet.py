# pip install retryz backoff
from __future__ import print_function
import random

import retryz
import backoff


def naughty_func():
    picky = random.randint(1, 3)
    if picky == 1:
        print('error')
        raise ValueError("Not good")
    elif picky == 2:
        raise RuntimeError("All bad")
    else:
        print('okay')


@retryz.retry(on_error=ValueError)
def retryz_call():
    naughty_func()


@retryz.retry(on_error=ValueError, limit=2)
def retryz_limit():
    naughty_func()


@backoff.on_exception(backoff.constant, ValueError,
                      interval=0, jitter=lambda: 0)
def backoff_call():
    naughty_func()


@backoff.on_exception(backoff.constant, ValueError,
                      interval=0, jitter=lambda: 0,
                      max_tries=2)
def backoff_limit():
    naughty_func()


def test_decorated(function, reraise=True):
    random.seed(1)
    for _ in range(30):
        print('--->{}'.format(function.__name__))
        try:
            function()
        except RuntimeError:
            print('rt error')
        except ValueError:
            if reraise: # pragma: nocover
                raise
            else:
                print('retry exceeded')


test_decorated(retryz_call)
test_decorated(retryz_limit, False)
test_decorated(backoff_call)
test_decorated(backoff_limit, False)
