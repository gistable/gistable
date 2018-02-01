__author__ = 'artemr'
'''
왜 파이썬 데코레이터를 만들때, @wraps어노테이션을 쓰는 것을 권장하는 걸까?
이유인 즉슨, 데코레이터 내부에서 인자로 전달받은 함수가 익명함수 처럼 취급되어 버리므로 디버깅이 난해해지는 단점이 있었기 때문이다.
자세한 설명은 아래의 링크에 첨부되어 있다.

원본: http://artemrudenko.wordpress.com/2013/04/15/python-why-you-need-to-use-wraps-with-decorators/
사본: https://www.evernote.com/shard/s174/sh/78eaad5f-a8f2-4496-b984-e3385fb963c0/922d9ab4b5cd23ac7b85aab42536aa4f
'''
 
from functools import wraps
 
 
def without_wraps(func):
    def __wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return __wrapper
 
def with_wraps(func):
    @wraps(func)
    def __wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return __wrapper
 
 
@without_wraps
def my_func_a():
    """Here is my_func_a doc string text."""
    pass
 
@with_wraps
def my_func_b():
    """Here is my_func_b doc string text."""
    pass
 
'''
# Below are the results without using @wraps decorator
print my_func_a.__doc__
>>> None
print my_func_a.__name__
>>> __wrapper
 
# Below are the results with using @wraps decorator
print my_func_b.__doc__
>>> Here is my_func_b doc string text.
print my_func_b.__name__
>>> my_func_b
'''