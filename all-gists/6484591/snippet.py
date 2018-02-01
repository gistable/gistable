#!/usr/bin/python
#coding:utf-8
#作者：Byron
#博客：http://jiabin.tk

import urllib2
import re

#定义程序主函数
def qiubai(page):
    url = "http://www.qiushibaike.com/week/page/%d" % page
    re_qb = re.compile(r'detail.*?<a.*?>(.*?)<.*?title="(.*?)">\s*(.*?)\s*?</',re.DOTALL)
    html = urllib2.urlopen(url).read()
    my_qiubai = re_qb.findall(html)
    n = len(my_qiubai)
    for i in range(n):
        for k in range(3):
            print my_qiubai[i][k]
        s = raw_input("回车继续")
        if s == "q":
            exit()
        print "-"*40

#定义程序循环体
def for_qb():
    for page in range(int(p),280):
        print "-"*18 + "第" + str(page) + "页" + "-"*18
        qiubai(page)

#该部分代码的目是为了设计的严谨，尽可能的使程序不发生崩溃
def if_qb():
    global p
    p = raw_input("输入要看的页数1~280:")
    if p == "q":
        exit()
    elif not p.isdigit() or p =="0" or int(p) > 280:
        if_qb()
    else:
        for_qb()
print "-"*40
print "糗百命令行版——Byron"
print "一入糗百深似海，从此节操是路人"
print '输入"q"退出程序'
print "-"*40

if_qb()