#-*- encoding: gb2312 -*-
import urllib2
from BeautifulSoup import BeautifulSoup
import threading

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-Agent' : user_agent}
#headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6)Gecko/20091201 Firefox/3.5.6'}
def getHtml(url):
    try:
        #req = urllib2.Request(url, headers)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req, None, 10)
        html = response.read()
        return html
    except Exception, e:
        print e
        return None

def getRssNew(url):
    print "url: " + url
    html = getHtml(url)
    if html:
        try:
            soup = BeautifulSoup(html)
        except:
            return None
        link = soup.find('link', rel="alternate")
        if link:
            href = link['href']
            if href and href[0] == '/':
                return url + href
            else:
                return href

def getUrlKey(url):
    pos = url.index('//')
    url = url[pos+2:]
    return url[:url.index('/')]

def getFriendsList(url):
    print "the main url: " + url
    friendsUrlList = []
    key = getUrlKey(url)
    html = getHtml(url)
    if html:
        try:
            soup = BeautifulSoup(html)
        except:
            return None
        for i in soup.findAll('li'):
            a = i.a
            if a and a.get('href') != None:
                href = a['href']
                if key not in href:
                    if href.startswith('http'):
                        print href
                        friendsUrlList.append(href)
    return friendsUrlList

def dump(filename, rsslist):
    print "begin dump"
    f = file(filename, 'w')
    for item in rsslist:
        f.write(item)
        f.write('\n')
    f.close()
    print "end dump"

def getUrlListFromFriends(urlList):
    friendsList = []
    for url in urlList:
        list = getFriendsList(url)
        if list:
            friendsList.extend(list)
    return friendsList

def getRssList(urlList):
    rssList = []
    for url in urlList:
        rss_url = getRssNew(url)
        if rss_url:
            print "rss: " + rss_url
            rssList.append(rss_url)
    return rssList

def getUrlListNew(file):
    urlList = []
    fh = open(file)
    for line in fh.readlines():
        line=line.strip('\n')
        urlList.append(line)
    return urlList

class Fetch(threading.Thread):
    def __init__(self, num, begin, end):
        threading.Thread.__init__(self)
        self._run_num = num
        self.begin = begin
        self.end = end

    def run(self):
        threadname = threading.currentThread().getName()
        print threadname
        for x in xrange(int(self.begin), int(self.end)):
            mutex.acquire()
            rssurl = getRssNew(urllist[x])
            if rssurl:
                print 'rss: ' + rssurl
                rssset.add(rssurl)
            mutex.release()


urllist = getUrlListNew('/home/jseanj/mygit/v2ex_crawl/all.txt')
rssset = set()
threads = []
num = 10
length = len(urllist)
n = int(length/num)
mutex = threading.Lock()

for x in xrange(0, num):
    begin = x*n
    end = begin + n
    if x == num-1:
        end = length
    threads.append(Fetch(x, begin, end))

for t in threads:
    t.start()

for t in threads:
    t.join()
    
dump('v2ex_rss', list(rssset))
