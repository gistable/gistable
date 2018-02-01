#!/usr/bin/env python

__copyright__ = 'Yuanxuan Wang <zellux at gmail dot com>'

from calibre.web.feeds.news import BasicNewsRecipe
from calibre.ebooks.BeautifulSoup import Tag, NavigableString
from collections import OrderedDict
from contextlib import nested, closing

import json
import re

class Zhihu(BasicNewsRecipe):

    INDEX = 'http://news.at.zhihu.com/api/1.1/news/latest'
    
    title = u'知乎日报'
    language = 'zh'
    __author__ = "Yuanxuan Wang"
    description = (u'知乎日报')
    no_stylesheets = True
    needs_subscription = False
    extra_css      = '''
      .headline { font-size: x-large; }
      .content { word-wrap: break-word; line-height: 1.6em; }
    '''

    def parse_index(self):
        opener = getattr(self.browser, 'open_novisit', self.browser.open)
        with closing(opener(self.INDEX)) as f:
            results = f.read()
        if not results:
            raise RuntimeError('Could not fetch index!')

        self.log(results)
        top_stories = []
        news = []
        json_obj = json.loads(results)
        for item in json_obj['news']:
            news.append(self.parse_article(item))
        for item in json_obj['top_stories']:
            top_stories.append(self.parse_article(item))
        return [(u'News', news), (u'Top Stories', top_stories)]

    def parse_article(self, item):
        return {
            'title': item['title'],
            'date': '',
            'description': '',
            'url': item['items'][0]['url']
        }
