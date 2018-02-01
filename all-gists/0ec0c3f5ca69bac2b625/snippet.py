# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from gevent import monkey; monkey.patch_all()

import re
from urlparse import urljoin

from gevent.pool import Pool
import requests
from scrapy.selector import Selector


download_re = re.compile(r'http://download.ted.com/talks/[^"]+')


def fetch_page(url):
    '''1. 웹페이지 다운로드'''
    r = requests.get(url)
    return r.text


def talk_links_from_listpage(url):
    '''2. 목록 페이지에서 강의 링크들 추출'''
    html = fetch_page(url)
    sel = Selector(text=html)
    talk_links = sel.css('.talk-link .media__message a::attr(href)').extract()
    talk_links = [urljoin(url, talk_link) for talk_link in talk_links]
    return talk_links


def talk_from_page(url):
    '''3. 강의 페이지에서 강의 메타정보 추출'''
    html = fetch_page(url)
    sel = Selector(text=html)
    download_m = download_re.search(html)
    return {
        'title': sel.css('.talk-hero__title::text').extract(),
        'description': sel.css('.talk-description::text').extract(),
        'download': download_m.group(0) if download_m else None,
    }


def latest_talks(page=1):
    '''4. 최근 강의 목록 반환'''
    list_url = 'http://www.ted.com/talks/browse?page={0}'.format(page)
    talk_links = talk_links_from_listpage(list_url)
    # talks = [talk_from_page(url) for url in talk_links]
    pool = Pool(20)
    talks = pool.map(talk_from_page, talk_links)
    return talks


from pprint import pprint
pprint(latest_talks())