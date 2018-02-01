#coding:utf-8
import random

def zundoko_generator():
    while True:
        yield random.choice(['ズン','ドコ'])

def zundoko_kiyoshi(generator):
    c = 0
    while True:
        zd = generator.next()
        print zd
        if zd == 'ズン':
            c += 1
        elif zd == 'ドコ':
            if c >= 4:
                break
            else:
                c = 0
    print 'キ・ヨ・シ！'

zundoko_kiyoshi(zundoko_generator())