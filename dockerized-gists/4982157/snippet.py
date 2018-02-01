# -*- coding=utf-8 -*-
__author__ = 'nephilim'
 
 
def curry(func, *args, **kwargs):
    """
    객체 생성 후 다음과 같이 p의 메서드에 대해 커링을 시도
    >>> p = Person()
    >>> p.name
    'lee'
    >>> curried = curry(p.yearsAfter, 10, 20)
    >>> curried(30)
    90
    """
 
    def curried_func(*nargs, **nkwargs):
        merged_kwargs = kwargs.copy()
        merged_kwargs.update(nkwargs)
        return func(*(args + nargs), **merged_kwargs)
    return curried_func
 
 
class Person(object):
    name = "lee"
    age = 30
    def yearsAfter(self, year1, year2, year3):
        return self.age + year1 + year2 + year3
 
 
if __name__ == '__main__':
    import doctest
    doctest.testmod()