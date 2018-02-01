# coding: utf-8
import os
import bottle
import requests
import PyRSS2Gen as gen
from datetime import timedelta, datetime
from multiprocessing.dummy import Pool
import urllib
import json

URL = 'http://bea.wufazhuce.com:7001/OneForWeb/one/get{}_N?strDate={}&strRow=1'
pool = Pool()


def get(url):
    return urllib.urlopen(url).read()


def parse(s):
    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')


def get(date):
    time = date.strftime('%Y-%m-%d')
    data = []

    jsons = pool.map(lambda c: json.load(urllib.urlopen(URL.format(c, time))),
                     ['C', 'Q', 'Hp'])

    t = jsons[0]['contentEntity']
    data.append(gen.RSSItem(title=t['strContTitle'],
                            author=t['strContAuthor'],
                            description=t['strContent'],
                            link=t['sWebLk'],
                            pubDate=parse(t['strLastUpdateDate']),
                            guid=gen.Guid('content' + t['strContentId'])))

    t = jsons[1]['questionAdEntity']
    data.append(gen.RSSItem(title=t['strQuestionTitle'],
                            author='',
                            description=(t['strQuestionContent'] + '<br/><br/>' +
                                         t['strAnswerTitle'] + '<br/>' +
                                         t['strAnswerContent']),
                            link=t['sWebLk'],
                            pubDate=parse(t['strLastUpdateDate']),
                            guid=gen.Guid('question' + t['strQuestionId'])))

    t = jsons[2]['hpEntity']
    data.append(gen.RSSItem(title=t['strHpTitle'],
                            author=t['strAuthor'],
                            description=('<a href="{}"><img src="{}"></a><br/>'.format(
                                t['strOriginalImgUrl'], t['strThumbnailUrl']) +
                                t['strContent']),
                            link=t['sWebLk'],
                            pubDate=parse(t['strLastUpdateDate']),
                            guid=gen.Guid('hp' + t['strHpId'])))
    return datetime.strptime(t['strMarketTime'], '%Y-%m-%d'), data


@bottle.route('/')
def index():
    t, data = get(datetime.now())

    rss = gen.RSS2(title=u'一个-韩寒',
                   link='http://wufazhuce.com/one/',
                   description='',
                   lastBuildDate=datetime.now(),
                   items=data)

    bottle.response.headers['Content-Type'] = 'text/xml; charset=UTF-8'
    return rss.to_xml(encoding='utf-8')

if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))