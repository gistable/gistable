from twisted.web import client
from twisted.internet import reactor, defer
from lxml import etree
from StringIO import StringIO
import re
import os

save_dir = "~/.video/tube8/"
base_url = "http://www.tube8.com"
download_re = re.compile("so.addVariable\('videoUrl',\s*'([\w\d.:/_]*)'\);", re.M)
url_re = re.compile("http://www\.tube8\.com/\w+/[-]*([\w\d_-]+)/(\d+)/",re.M)

q = []
dlist = []
is_run = True
dl = None

def error(e, url):
    print("%s is failure." % url)
    print(e)

def dl_error(e, url):
    print("%s is failure. retain %d" % (url, len(q)))
    print(e)
    if q:
        download(q.pop())
    else:
        global dl
        def stop(res):
            global is_run
            if is_run:
                reactor.stop()
                is_run = False

        if not dl:
            dl = defer.DeferredList(dlist)
            dl.addCallback(stop)

def finish(result, url):
    print("finish %s retain %d" % (url, len(q)))
    if q:
        download(q.pop())
    else:
        global dl
        def stop(res):
            global is_run
            if is_run:
                reactor.stop()
                is_run = False

        if not dl:
            dl = defer.DeferredList(dlist)
            dl.addCallback(stop)

def download(data):
    url, save_path = data
    d = client.downloadPage(url, save_path, supportPartial=1)
    dlist.append(d)
    d.addCallback(finish, url).addErrback(dl_error, url);


def contents(data, href):
    n = url_re.search(href)
    name = ''
    if n:
        name = n.group(1)
        name = name + n.group(2)

    m = download_re.search(data)
    if m:
        url = m.group(1)
        ext = url[url.rfind("."):]
        filename = name + "_tube8" + ext
        save_path = os.path.join(save_dir, filename)
        #print(url)
        #print(save_path)
        q.append((url,save_path))

        
pages = set()

def get_list(data, page_link):
    parser = etree.HTMLParser()
    root = etree.parse(StringIO(data), parser)
    links = root.findall(".//a[@href]")
    defList = []
    for e in links:
        href = e.attrib['href']

        if "/search.html" in href and e.text == ">":
            pages.add(href)
        elif url_re.search(href) and 'onmouseover' not in e.attrib:
            print(href)
            d = client.getPage(href)
            defList.append(d)
            d.addCallback(contents, href).addErrback(error, href)
    
    def next(result):
        if pages:
            page = pages.pop()
            print("-" * 80)
            print(page)
            get_search_result(page, True)
        else:
            q.reverse()
            for i in xrange(5):
                download(q.pop())

    dl = defer.DeferredList(defList)
    dl.addCallback(next)


def search(word):
    #url = base_url + "/search.html?q=%s" % word
    url = base_url + "/search.html?q=%s&page=1" % word
    get_search_result(url, True)

def get_search_result(url, page_link):
    client.getPage(url).addCallback(get_list, page_link).addErrback(error, url)


search('japanese')

reactor.run()
