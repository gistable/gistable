#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by i@BlahGeek.com at 2014-01-01

def pi_generate():
    """
    returns a single digit of pi each time iterated
    """
    q, r, t, k, m, x = 1, 0, 1, 1, 3, 3
    while True:
        if 4 * q + r - t < m * t:
            yield m
            q, r, t, k, m, x = \
            (10*q, 10*(r-m*t), t, k, (10*(3*q+r))//t - 10*m, x)
        else:
            q, r, t, k, m, x = \
            (q*k, (2*q+r)*x, t*x, k+1, (q*(7*k+2)+r*x)//(t*x), x+2)


if __name__ == '__main__':
    match_str = '2014'
    match_len = len(match_str)
    last_str = '0' * match_len
    for i,x in enumerate(pi_generate()):
        last_str = last_str[1:] + str(x)
        if i % 100 == 0:
            print i  # for debug
        if last_str == match_str:
            print 'done!', i - match_len + 1
            break
