# -*- coding:utf-8 -*-
import requests, os, re, sys, time
from time import sleep
from threading import Thread

reload(sys)
sys.setdefaultencoding('utf8')

UPDATE_INTERVAL = 0.01

class URLThread(Thread):
    def __init__(self, url, timeout=10, allow_redirects=True):
        super(URLThread, self).__init__()
        self.url = url
        self.timeout = timeout
        self.allow_redirects = allow_redirects
        self.response = None

    def run(self):
        try:
            self.response = requests.get(self.url, timeout = self.timeout, allow_redirects = self.allow_redirects)
        except Exception , what:
            print what
            pass

def multi_get(uris, timeout=10, allow_redirects=True):
    '''
    uris    uri列表
    timeout 访问url超时时间
    allow_redirects 是否url自动跳转
    '''
    def alive_count(lst):
        alive = map(lambda x : 1 if x.isAlive() else 0, lst)
        return reduce(lambda a,b : a + b, alive)
    threads = [ URLThread(uri, timeout, allow_redirects) for uri in uris ]
    for thread in threads:
        thread.start()
    while alive_count(threads) > 0:
        sleep(UPDATE_INTERVAL)
    return [ (x.url, x.response) for x in threads ]

class Copyer(object):
    def __init__(self, r):
        self.response = r
        self.baseurl = r[0]
        self.home = self.baseurl.split('/')[2]
        self._create_dir()
        self.download()

    def download(self):
        '''下载'''
        _need = self.get_allthings_need_to_download()
        print 'Begin write index.html'
        open('%s/index.html'%self.home,'w').write(_need[1])
        _responses = multi_get(_need[0])
        self._download_files(_responses)

    def get_allthings_need_to_download(self):
        '''获取所有要下载的链接'''
        _content = self.response[1].text
        _links = self._get_links_from_content(_content)
        return self._get_fullpath_links(_links, _content)

    def link_alias(self, link):
        link = self.full_link(link)
        name = link.rsplit('/',1)[1]
        if '.css' in name:
            name = name[:name.find('.css')+4]
            return '/media/css/%s'%name
        elif '.js' in name:
            name = name[:name.find('.js')+3]
            return '/media/js/%s'%name
        else:
            return '/media/image/%s'%name

    def strip_link(self, link):
        if link and (link[0] in ['"',"'"]):
            link = link[1:]
        while link and (link[-1] in ['"',"'"]):
            link = link[:-1]
        while link.endswith('/'):
            link = link[:-1]
        if link and (link[0] not in ["<","'",'"']) and ('feed' not in link):
            return link
        else:
            return ''

    def full_link(self,link,baseurl=None):
        if not baseurl:
            baseurl = self.baseurl
        if '?' in link:
            link = link.rsplit('?',1)[0]
        if not link.startswith('http://'):
            if link.startswith('/'):
                link = '/'.join(baseurl.split('/',3)[:3]) + link
            elif link.startswith('../'):
                while link.startswith('../'):
                    baseurl = baseurl.rsplit('/',2)[0]
                    link = link[3:]
                link = baseurl+'/'+link
            else:
                link = baseurl.rsplit('/',1)[0]+'/'+link
        return link

    def _download_files(self, responses, depth=3):
        '''下载js、image等文件到目录'''
        for url, data in responses:
            if url.endswith('.css'):
                self._download_css(url, data, depth)
            else:
                try:
                    _filepath = '%s%s'%(self.home, self.link_alias(url))
                    print 'Writing %s'%_filepath
                    open(_filepath, "wb").write(data.content)
                except Exception,what:
                    print what

    def _download_css(self, url, data, depth):
        '''下载css文件，深入3层'''
        try:
            _content = data.content
        except Exception,what:
            print what
            return
        if depth>0:
            links = re.compile(r'url\([\'"]?(.*?)[\'"]?\)').findall(_content)
            templinks = []
            _list = []
            for link in links:
                slink = self.strip_link(link)
                if slink:
                    templinks.append(slink)
            links = templinks
            for link in set(links):
                _list.append(self.full_link(link, url))
                _content = _content.replace(link, self.link_alias(link)[1:].replace("media",".."))

            try:
                _filepath = '%s%s'%(self.home, self.link_alias(url))
                print 'Writing %s'%_filepath
                open(_filepath, "wb").write(_content)
            except Exception,what:
                print what
            if _list:
                self._download_files(multi_get(_list), depth-1)

    def _create_dir(self):
        '''创建域名为名的目录,如存在删除旧目录'''
        if os.path.exists(self.home):
            os.rename(self.home, '%s%s'%(self.home, time.time()))
        try:
            os.mkdir(self.home)
            os.mkdir(self.home+'/media')
            os.mkdir(self.home+'/media/js')
            os.mkdir(self.home+'/media/css')
            os.mkdir(self.home+'/media/image')
        except Exception,what:
            print what

    def _get_links_from_content(self, content):
        '''获取页面中所有css、js、image链接'''
        links = re.compile(r'<link[^>]*href=(.*?)[ >]', re.I).findall(content)
        links.extend( re.compile(r'<script[^>]*src=(.*?)[ >]',re.I).findall(content))
        links.extend( re.compile(r'<img[^>]*src=(.*?)[ >]',re.I).findall(content))
        return self._get_strip_links(links)

    def _get_strip_links(self, links):
        _templinks = []
        for link in links:
            slink = self.strip_link(link)
            if slink:
                _templinks.append(slink)
        return _templinks

    def _get_fullpath_links(self, links, content):
        _templinks = []
        for link in set(links):
            content = content.decode('utf8')
            content = content.replace(link, self.link_alias(link)[1:])
            content = content.replace(u'charset=gb2312', 'charset=utf-8')
            content = content.replace(u'charset=GB2312', 'charset=utf-8')
            content = content.replace(u'charset=gbk', 'charset=utf-8')
            content = content.replace(u'charset=GBK', 'charset=utf-8')
            _templinks.append(self.full_link(link))
        return _templinks, content


if __name__ == '__main__':
    r = multi_get(['http://www.au92.com'])
    _copyer = Copyer(r[0])
