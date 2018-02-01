#-*- coding:utf-8 -*-
from BeautifulSoup import BeautifulSoup as b

from urllib import quote_plus as q, unquote_plus as unq, urlencode
from urllib2 import build_opener, urlopen, HTTPCookieProcessor
from cookielib import CookieJar
import urlparse
import re

__author__ = 'bluele'

BASE_URL = 'https://www.google.co.jp'
BASE_SEARCH_URL = BASE_URL + '/searchbyimage?%s'

REFERER_KEY = 'Referer'

Opener = build_opener(HTTPCookieProcessor(CookieJar()))
Opener.addheaders = [
    ('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'),
    ('Accept-Language','ja,en-us;q=0.7,en;q=0.3')
]

image_url_pattern = re.compile(ur'^http://www.google.co.jp/imgres\?imgurl=(?P<url>[^&]+)')

def get_referer_index():
    i = 0
    for k, v in Opener.addheaders:
        if k == REFERER_KEY:
            return i
        i += 1
    else:
        return None


def get_referer():
    cur = get_referer_index()
    if cur is not None:
        return Opener.addheaders[cur]
    else:
        return None


def set_referer(url):
    cur = get_referer_index()
    if cur is not None:
        del Opener.addheaders[cur]
    Opener.addheaders.append(
        (REFERER_KEY, url)
    )


def search_image(url):
    params = {
        'image_url': url,
        'hl': 'ja',
        }
    query = BASE_SEARCH_URL % urlencode(params)
    f = Opener.open(query)
    url = f.url
    # domain
    # url += '&as_sitesearch=zozo.jp'
    f = Opener.open(url)
    html = f.read()
    set_referer(f.url)
    return html


def get_similar_image_urls(html):
    soup = b(html)
    for item in soup.find('div', {'id': 'iur'}).findAll('a', {'class': 'bia uh_rl'}):
        url = item.get('href')
        yield urlparse.parse_qs(urlparse.urlparse(url).query)['imgurl']


def main():
    import sys
    url = sys.argv[1]
    html = search_image(url)
    for url in get_similar_image_urls(html):
        print url


if __name__ == '__main__':
    main()
