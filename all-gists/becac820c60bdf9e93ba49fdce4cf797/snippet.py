# Read docs here: https://docs.python.org/3/library/contextlib.html
>>> from contextlib import contextmanager
>>>
>>>
>>> @contextmanager
... def deco_and_cm():
...     print('Hello')
...     yield
...     print('Goodbye')
...
>>>
>>> with deco_and_cm():
...     print('Nice to meet you!')
...
Hello
Nice to meet you!
Goodbye
>>>
>>> @deco_and_cm()
... def fun(name):
...     print('Nice to meet you, %s!' % name)
...
>>>
>>> fun('Tomek')
Hello
Nice to meet you, Tomek!
Goodbye
>>>