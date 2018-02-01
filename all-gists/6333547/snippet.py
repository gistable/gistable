#encoding: utf-8

__author__ = 'Dodola'
from lxml.html import parse
from time import sleep,ctime
import time
import urllib.request
import threading
import contextlib
import queue
import os
from urllib.parse import (
    urlparse, urlsplit, urljoin, unwrap, quote, unquote,
    splittype, splithost, splitport, splituser, splitpasswd,
    splitattr, splitquery, splitvalue, splittag, to_bytes, urlunparse)

BASEURL = "http://www.topit.me"
ALBUMURL="http://www.topit.me/album/"
ALBUMPERURL="http://www.topit.me/album/%s?p=%s"
USERURL="http://www.topit.me/user/"
USERPERURL="http://www.topit.me/user/%s?p=%s"

def urlretrieve(url, filename=None, reporthook=None, data=None):

    url_type, path = splittype(url)
    
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = { 'User-Agent' : user_agent }
    req = urllib.request.Request(url, data,headers);
    with contextlib.closing(urllib.request.urlopen(req)) as fp:
        headers = fp.info()


        if url_type == "file" and not filename:
            return os.path.normpath(path), headers

        # Handle temporary file setup.
        if filename:
            tfp = open(filename, 'wb')
        else:
            tfp = tempfile.NamedTemporaryFile(delete=False)
            filename = tfp.name
            _url_tempfiles.append(filename)

        with tfp:
            result = filename, headers
            bs = 1024*8
            size = -1
            read = 0
            blocknum = 0
            if "content-length" in headers:
                size = int(headers["Content-Length"])

            if reporthook:
                reporthook(blocknum, 0, size)

            while True:
                block = fp.read(bs)
                if not block:
                    break
                read += len(block)
                tfp.write(block)
                blocknum += 1
                if reporthook:
                    reporthook(blocknum, len(block), size)

    if size >= 0 and read < size:
        raise ContentTooShortError(
            "retrieval incomplete: got only %i out of %i bytes"
            % (read, size), result)

    return result

def Download(path, pageUrl):
    
    #try:
    spath = parse( pageUrl)
    imageUrls = spath.xpath('//a[@id="item-tip"]')
    imageUrl = imageUrls[0].attrib["href"]
    print("正在下载%s\n"%imageUrl)
    imageNames=imageUrl.rsplit('/')
    imageName=imageNames[len(imageNames)-1]
    urlretrieve(imageUrl, path+imageName)
    print("保存成功:%s%s\n"%(path ,imageName))
    #except Exception as err:
    #    print("下载错误{0}\n".format(err))
        


def DownloadUser(path,userid):
    pageUrl=USERURL+userid
    tempdir="%s%s\\"%(path,time.strftime("%Y%m%d%H%M%S",time.localtime(time.time())))
    print(tempdir)
    os.mkdir(tempdir)
    print(pageUrl)
    spath=parse(pageUrl)
    pagecounts=spath.xpath("id('pagination')/div/a")
    print(pagecounts)
    print("页面总数:%s"%(int(pagecounts[len(pagecounts)-2].text_content())))
    if len(pagecounts)>1:
        pagecount=int(pagecounts[len(pagecounts)-2].text_content())
    else:
        pagecount=2
    for page in range(1,pagecount):
        print("访问第%s页"%page)
        DownloadPerUser(tempdir,userid,page)

def DownloadPerUser(path,userid,page):
    pageUrl=USERPERURL% (userid,page)
    pageel=parse(pageUrl)
    imgUrls=pageel.xpath("//a[starts-with(@href,'http://www.topit.me/item/')]/@href")
    imgUrls=set(imgUrls)#去重
    print("第%s页图片数%s"%(page,len(imgUrls)))
    task_threads=[] #存储线程
    count=1
    for i in imgUrls:
        t= threading.Thread(target=Download,args=(path,i))
        #Download(path,i.attrib.get("href"))
        count=count+1
        task_threads.append(t)
    for task in task_threads:
        task.start()
        task.join()#将线程改为1，过多线程会被封
    for task in task_threads:
        task.join() #等待所有线程结束
    print("线程结束")


def DownloadAlbum(path,albumId,page=1):
    pageUrl=ALBUMURL+albumId
    tempdir="%s%s\\"%(path,time.strftime("%Y%m%d%H%M%S",time.localtime(time.time())))
    print(tempdir)
    os.mkdir(tempdir)
    print(pageUrl)
    spath=parse(pageUrl)
    pagecounts=spath.xpath("id('pagination')/div/a")
    print(pagecounts)
    print("页面总数:%s"%(int(pagecounts[len(pagecounts)-2].text_content())))
    if len(pagecounts)>1:
        pagecount=int(pagecounts[len(pagecounts)-2].text_content())
    else:
        pagecount=2
    task_threads=[] #存储线程
    for page in range(page,pagecount+1):
        print("访问第%s页"%page)
        t= threading.Thread(target=DownloadPerAlbum,args=(tempdir,albumId,page))
        task_threads.append(t)
        #DownloadPerAlbum(tempdir,albumId,page)
        
    for task in task_threads:
        task.start()

    for task in task_threads:
        task.join() #等待所有线程结束
  
    

def DownloadPerAlbum(path,albumid,page):
    pageUrl=ALBUMPERURL% (albumid,page)
    pageel=parse(pageUrl)
    imgUrls=pageel.xpath("//a[starts-with(@href,'http://www.topit.me/album/%s/item/')]/@href"%albumid)
    imgUrls=set(imgUrls)#去重
    print("第%s页图片数%s"%(page,len(imgUrls)))
    for i in imgUrls:
        Download(path,i)
##    task_threads=[] #存储线程
##    count=1
##    for i in imgUrls:
##        t= threading.Thread(target=Download,args=(path,i))
##        count=count+1
##        task_threads.append(t)
##    for task in task_threads:
##        task.start()
##       # task.join()#将线程改为1，过多线程会被封
##    for task in task_threads:
##        task.join() #等待所有线程结束
##    print("线程结束")
    
##    for i in imgUrls:
##        print("===add job====")
##        work_manager.add_job(Download,[path,i]);

def testMe(args):
    print(args)
    time.sleep(1)
     
DownloadAlbum("l:\\topit.me\\","1310049")

#DownloadUser("l:\\topit.me\\","965126")
    
