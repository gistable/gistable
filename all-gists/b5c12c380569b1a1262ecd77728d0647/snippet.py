#!/usr/bin/python
# -*- coding:utf-8 -*-

import threading
import requests
import re
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from lxml import etree

reload(sys)
sys.setdefaultencoding("utf-8")

# 下载目录
Directory = '/opt/www/images/'
# 存储获取开始网页地址的地址
start_url = 'http://jandan.net/ooxx'
# 存储User-Agent
header = []
# 存储开始网页地址
start_page = None
# 线程上限
Maxthreads = 4
# 存储线程数量
threadnum = None
# 线程容器
allthread = []
# 存储爬取的页数
numberOfPages = None


# 获得 UserAgentString
def obtainAgentStrings():
    h = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
    }
    r = requests.get(
        'http://useragentstring.com/pages/useragentstring.php?typ=Browser',
        headers=h)
    source = etree.HTML(r.text)
    return [{'User-Agent': i} for i in source.xpath('//li/a/text()')]


# 抓取函数
def main(page):
    for i in range(len(header)):
        if header_Available[i] != False:
            url = start_url + '/page-' + str(page) + '#comments'
            r = requests.get(url, headers=header[i])
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, "html5lib")
            if soup.find(text=re.compile('屏蔽')) == None:
                print('=============================')
                print('正在下载第 ' + str(page) + ' 页')
                # 存储包含图片地址的标签
                img = []
                imgall = soup.body('li', id=re.compile("comment-"))
                for tmp in imgall:
                    img += tmp.div.find(
                        'div', class_='row').find(
                        'div', class_='text').find_all(
                        'img', src=True)
                for n, girl in enumerate(img):
                    if not girl.has_attr('org_src'):
                        url = "http:"+girl['src']
                        # 保存图片新浪图床地址
                        with open('jandan-sinaimg-url.txt','a+') as f:
                            print >>f,url,'\t',str(page)
                        # 保存图片名称，形如 Directory 下 jandan.net-2420-25-006cuHWfgy1fdh09j49ysj32e836o7wj.jpg
                        with open(Directory + 'jandan.net' +'-'+ str(page) + '-' + str(n)+ '_'+ url.split('/')[4], 'wb') as f:
                            f.write(requests.get(url).content)
                    else:
                        url = "http:"+girl['org_src']
                        # 保存图片新浪图床地址
                        with open('jandan-sinaimg-url.txt','a+') as f:
                            print >>f,url,'\t',str(page)
                        with open(Directory + 'jandan.net' +'-'+ str(page) + '-' + str(n) + '_'+ url.split('/')[4], 'wb') as f:
                            f.write(requests.get(url).content)
                    print('正在下载第 ' + str(n) + ' 张'+'\n'+ url+'.....OK!')
                print('第 ' + str(page) + ' 页下载完成啦！！！')
                return True
            else:
                if header_Available[i] != False:
                    header_Available[i] = False
                    print('被屏蔽，正在反屏蔽.....\n        User-Agent 可用信息:')
                    if header_Available[-1] == False:
                        print('反屏蔽失败,线程终止!\nUser-Agent 可用信息:')
                        return False


# 创建多线程
def creatBackGroundThreads():
    for i in range(threadnum):
        allthread.append(Async(start_page - i - 1))
        allthread[i].start()


# 当前线程
def currentThreads():
    if numberOfPages != 0:
        for pages in range(start_page, start_page - numberOfPages,
                           -1 - threadnum):
            if header_Available[-1] != False:
                main(pages)
            else:
                return False


# 多线程类
class Async(threading.Thread):
    def __init__(self, h_page):
        threading.Thread.__init__(self)
        self.h_page = h_page

    def run(self):
        for pages in range(self.h_page, start_page - numberOfPages,
                           -1 - threadnum):
            if header_Available[-1] != False:
                main(pages)
            else:
                return False
# 计时开始
start = datetime.now()
header = obtainAgentStrings()

# Init User-Agent可用信息
header_Available = [None for i in range(len(header))]


# 获得 start_page
for i in range(len(header)):
    rs = requests.get(start_url, headers=header[i])
    rs.encoding = 'utf-8'
    soups = BeautifulSoup(rs.text, "html5lib")
    if soups.find(text=re.compile('屏蔽')) == None:
        start_page = int(
            soups.body.find(
                'span', class_='current-comment-page').contents[0][1:-1])
        numberOfPages = int(input('输入爬取的页数: '))
        threadnum = int(input('输入线程数(线程数量上限' + str(Maxthreads) + '): ')) % (
            Maxthreads + 1) - 1
        if threadnum < 0:
            threadnum = 0
        break
    else:
        header_Available[i] = False
        print('被屏蔽，正在反屏蔽.....\n        User-Agent 可用信息:')
    if header_Available[-1] == False:
        print('反屏蔽失败!\nUser-Agent 可用信息:')

if header_Available[-1] != False:
    creatBackGroundThreads()
    currentThreads()
    for m in allthread:
        m.join()

    #   计时结束
    end = datetime.now()
    if header_Available[-1] != False:
        print('\n!!!!!抓取完毕!!!!!!\n花费时间：' + str(end - start))
    else:
        print('!!!!!部分图片未能抓取!!!!!')
else:
    print('!!!!不能进行抓取!!!!!')
