#-*- coding:utf-8 -*-
u'''
関数合成みたいな何か
'''


class Composable(object):
    u'''
    合成可能
    '''

    def __init__(self, funcs):

        self.functions = funcs


    def __and__(self, func):

        return Composable(self.functions+[func])


    def __call__(self, *args, **argd):

        rev = list(reversed(self.functions))

        car = rev[0]
        cdr = rev[1:]

        return reduce(lambda x, y: y(x),
                      cdr, car(*args, **argd))


def composable(f):
    u'''
    デコレータちゃん
    '''
    
    return Composable([f])



if __name__ == '__main__':


    @composable
    def add1(v):
        return v + 1

    @composable
    def mul2(v):
        return v * 2

    print (mul2 & add1 & add1 & add1)(10) # (10 + 1 + 1 +1) * 2
    print (add1 & add1 & add1 & mul2)(10) # 10 * 2 + 1 + 1 + 1


