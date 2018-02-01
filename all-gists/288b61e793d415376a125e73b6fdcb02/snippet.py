#! /usr/bin/env python
# -*- coding: utf-8 -*-

## This file contains a list of cool one-liners in python.
## I will update the list occasionally.
## You are welcome to suggest new oneliners in the comments.
## Tested on python 2.7

# Perfect Numbers
print [n for n in range(10000) if n==sum(d for d in range(1,n/2+1) if not n%d)]

# Number of On bits
f=lambda n:n%2+f(n>>1) if n!=0 else 0
print map(f, range(10))
