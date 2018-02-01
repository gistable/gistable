#!/usr/bin/env python
# encoding: utf-8
"""
re.py

Created by mmiyaji on 2012-08-27.
Copyright (c) 2012  ruhenheim.org. All rights reserved.
"""

import sys, os, re

def execReg(reg, text):
    # コンパイルフラグ multiline(re.M) を追加、文字列内改行を考慮する
    p = re.compile(reg, re.M)
    print p.findall(text)

def main():
    text = """keyword1:1
keyword2:2
keyword1:3
keyword3:4
keyword2:5
"""
    print "検索対象文字列: ", text
    print "シンプルに値だけを抽出する場合: ",
    execReg("^keyword1:(.*)", text)

    print "キーとバリューをタプルとして抽出する場合: ",
    execReg("(^keyword1):(.*)", text)

    print "要素を名前付きグループとして抽出する場合: ",
    execReg("(?P<key>^keyword1):(?P<value>.*)", text)

    print "keyword+数字なペアを抽出: ",
    execReg("(?P<key>^keyword\d+):(?P<value>.*)", text)

if __name__ == '__main__':
    main()

"""
実行結果:
$ python re.py                                                                                                                                              [ /tmp ]
検索対象文字列:  keyword1:1
keyword2:2
keyword1:3
keyword3:4
keyword2:5

シンプルに値だけを抽出する場合:  ['1', '3']
キーとバリューをタプルとして抽出する場合:  [('keyword1', '1'), ('keyword1', '3')]
要素を名前付きグループとして抽出する場合:  [('keyword1', '1'), ('keyword1', '3')]
keyword+数字なペアを抽出:  [('keyword1', '1'), ('keyword2', '2'), ('keyword1', '3'), ('keyword3', '4'), ('keyword2', '5')]
"""