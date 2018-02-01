from bs4 import BeautifulSoup
import urllib
import os
import re

qvod_link_reg = re.compile(ur'qvod://[0-9]{9}\|[A-Z0-9]{40}\|[\u4e00-\u9fa50-9]+\.')
main_url = 'http://www.qvodzy.me'

def matchURL(url):
    res = urllib.urlopen(url)
    print 'match ',url
    soup = BeautifulSoup(res.read().decode('gb2312','ignore'))

    return soup.find_all('a')



def getUrlContent(url):
    reg = re.compile(ur'http://www\.[0-9a-zA-z]\.\.zip')
    if url.endswith('.rar'):
        print 'rar'
        return None
        
    
    res = urllib.urlopen(url.strip())
    content = []
   # print res.read()
    soup = BeautifulSoup(res.read().decode('gb2312','ignore'))
    for link in soup.find_all('a'):
       s = link.string
       #print link.get('href')
       if s is not None and qvod_link_reg.match(s):
            content.append(s.encode('gb2312'))
       elif s is not None:
            if(link.get('href').startswith('http://www.qvodzy.me')):
                processURL(link.get('href'))
            else:
                pass
    return content

def processURL(main_url):
    reg = re.compile(ur'http://www\.[0-9a-zA-z]\.\.zip')
    if main_url.endswith('.rar'):
        print 'rar'
        return None
    
    hrefs = matchURL(main_url)
    
    for link in hrefs:
        href = link.get('href').strip()
        reg = re.compile(ur'http://')
        regadd = re.compile(ur'qvodadd://')
        regcha = re.compile(ur'qvodcha://')
        reg115 = re.compile(ur'http://115')
        regjs = re.compile(ur'javascript:')
        if  reg.match(href) or regadd.match(href) or regcha.match(href) or reg115.match(href) or regjs.match(href):
            print 'pass'
            #pass
        elif href is not None:
             full_url = main_url + href
             print full_url
             qvod_url = getUrlContent(full_url)
             if qvod_url is not None:
                for line in qvod_url:
                    print line
            
if __name__=="__main__":
    #htmlr = getUrlContent("http://www.qvodzy.me/movie.asp?ID=22369")
    processURL(main_url)
    #for link in htmlr.find_all('a'):
     #   print (link.string)
