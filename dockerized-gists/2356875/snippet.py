#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from BeautifulSoup import * 
import urllib2
import codecs

def urlToTxt(url):
    bookUrl = url
    suffix = "html"
    if url[-3:] == 'htm':
        suffix = 'htm'
    source = urllib2.urlopen(bookUrl)
    rootSoup = BeautifulSoup(source.read())
    
    charpterNum = rootSoup.findAll('a', href=re.compile(u'[0-9]+(?:\.[0-9]*)?.'+suffix))
    charpterNum = len(charpterNum) - 1

    links = rootSoup.find('td', { "class" : "tt2" }).findAll('a')

    bookName = rootSoup.find('title').contents[0][:-9]
    
    print u'书的名字是 ' + bookName
    print u'共有 ' + str(charpterNum) + u' 章节'
    
    f = codecs.open(bookName+u".txt", 'w', 'utf-8')
    for i in links:
        if i['href'] == 'http:/www.tianyabook.com':
            continue
        f.write('\n\r'+'------------------------------------------')
        f.write('\n\r'+i.contents[0]+'\n\r')
        f.write(getStrFromUrl(url[:-6-len(suffix)]+i['href']))
    f.close();

def getStrFromUrl(url):
    print u'正在获取' + url
    result = u''
    f = urllib2.urlopen(url)
    pageSoup = BeautifulSoup(f.read().decode("GB18030"))
    text = pageSoup.find('table', width='586').findAll(text=True)
    for i in text:
        if i == "\n":
            continue
        elif i == '&nbsp;':
            #result += '\n\r' 
            continue
        else :
            i = i.replace('&nbsp;','')
            result += i
            result += '\n\r'
    return result

if __name__ == "__main__":
    #urlToTxt("http://www.tianyabook.com/zw/shijieyinnibutong/index.html")
    #getStrFromFile("32.html")
    print '输入书籍目录URL'
    url = raw_input()
    urlToTxt(url)
    print '生成完毕'
