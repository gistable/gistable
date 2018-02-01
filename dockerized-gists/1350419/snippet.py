#!/usr/bin/env python
# -*- coding: utf-8 -*-


import operator
import itertools
import re

def debug(x):
    print 'debug', dir(x), x.group()

def convert1(sent):
    # too bad
    assert isinstance(sent, unicode), "not support non-unicode yet"
    def quote_gen(quotes=u"“”"):
        yield u""
        while 1:
            yield quotes[0]
            yield quotes[1]

    seg = sent.split('"')
    if len(seg) % 2 != 1:
        # raise RuntimeError('non-balenced quotes!')
        return "ERROR"
    newseg = reduce(tuple.__add__, zip(quote_gen(), seg ))
    newsent = reduce(unicode.__add__, newseg)
    return newsent

def convert2(sent):
    trans_table = {':': u'：', ',': u'，', '.': u'。',
                   '?': u'？', '!': u'！', ';': u'；',}
    # '"': u'＂', "'": u'＇'}
    for k in trans_table.keys():
        trans_table[ord(k)] = trans_table[k] # make a transtable

    dquotes = itertools.cycle(u'“”' if sent.count('"') & 1 == 0 else u'＂')
    squotes = itertools.cycle(u'‘’' if sent.count("'") & 1 == 0 else u'＇')
    _obj = lambda x: dquotes.next() if '"' == x.group() else squotes.next()
    pattern = re.compile(ur'''['"]''', re.U)
    newsent = pattern.sub(_obj, sent)

    return newsent.translate(trans_table)



def test(msg):

    print "msg =>", msg
    print "convert1(msg) =>", convert1(msg)
    print "convert2(msg) =>", convert2(msg)

def pk():
    msg = u'基本原则"这"是一个"测试用例".' * 1000
    return msg

if __name__ == '__main__':
    test( u'基本原则"这"是一个"测试用例".' )
    test( u'''基本原则"这"是一个"'测试'用例"''' )
    test( u'''昨日,玉溪市公安局红塔分局驻"高古楼网站"警长李正平表示,目前警方已介入调查此事.''')
    test( u'测试, "这是"一"个"错误测试用例"')
    test( u'""""""""""""')
