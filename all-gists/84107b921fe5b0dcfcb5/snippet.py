#!/usr/bin/env python
# rot5
# uobis.com

rpin = raw_input('Enter PIN: ')

def rot5(s):
    x = []
    for i in s:
        j = ord(i)
        if j >= 48 and j <= 57:
            if j <= 52:
                x += chr(j + 5)
            else:
                x += chr(j - 5)
        else:
            x += i
    return ''.join(x)
    
roto = rot5(rpin)

print roto