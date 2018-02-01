#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import json
import urllib2
from urllib import urlencode
import json
import os
import os.path
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


reportFile = "/tmp/news_result.html"
if os.path.exists(reportFile):
    os.remove(reportFile)

maxNews = raw_input("Сколько новостей просмотреть (кратно 200, по умолчанию 200, нет смысла указывать более 1000 новостей): ")
if maxNews == '':
    maxNews = '200'
iterations = int(maxNews) // 200
print "Ищу в",iterations, "проход"
searchFor = "сдам квартиру"
searchInput = raw_input("Введите строку для поиска (сдам квартиру): ")
if searchInput == '':
    searchInput = searchFor
print "Ищу по строке -", searchInput

newsNum = 200

def call_api(method, params):
    if isinstance(params, list):
        params_list = [kv for kv in params]
    elif isinstance(params, dict):
        params_list = params.items()
    else:
        params_list = [params]
    url = "https://api.vk.com/method/%s?%s" % (method, urlencode(params_list))
    return urllib2.urlopen(url).read()


def get_news(offset):
    return call_api("newsfeed.search", [("q", searchInput), ("count", newsNum), ("offset", offset)])
def get_user(uid):
    return call_api("users.get", [("uids", uid), ("fields", "city")])
def get_cities(country, q):
    return call_api("places.getCities", [("q", q), ("country", country)])
def get_cities_byID(id):
    return call_api("places.getCityById", ("cids", id))


cityInput = raw_input("Введите часть названия города для поиска, или просто нажмите enter: ")
cities = get_cities(1, cityInput)
cities = json.loads(cities, encoding = "utf-8")['response']
print "\n".join("%d. %s" % (num + 1, city["title"]) for num, city in enumerate(cities))
choise = -1
choise = int(raw_input("Выберите номер города: ")) - 1

htmlFile = open(reportFile, 'w')
print >> htmlFile, '<table border=1>'

def printTd(repValue):
    print >> htmlFile, '<td>'
    print >> htmlFile, repValue
    print >> htmlFile, '</td>'

def printTdHref(link,repValue):
    print >> htmlFile, '<td>'
    print >> htmlFile, '<a href="',link,'">',repValue,'</a>'
    print >> htmlFile, '</td>'

offset = 0
counter = 0
for iter in range(1,iterations+1):


    news = get_news(offset)
    news = json.loads(news, encoding = "utf-8")

    print "Я запросил и получил ", newsNum*iter, "новостей"
    print "Ищу новости с автором частным лицом из запрошенного города - ", cities[choise]['cid']
    for i in range(1,newsNum+1):
  # Now we are cheking that user is not group (his ID must be positive)
	try:
	    if news['response'][i]['owner_id'] > 0:
		# now we should get info about user and check his city
		user=get_user(news['response'][i]['owner_id'])
		user=json.loads(user, encoding = "utf-8")
		if 'city' in user['response'][0] and user['response'][0]['city'] <> '0':
		    cityName=get_cities_byID(user['response'][0]['city'])
		    cityName=json.loads(cityName, encoding = "utf-8")
		    cityName['response'][0]['name']
		    print i+offset,"Нашел новость из города ", user['response'][0]['city'], "-", cityName['response'][0]['name'], " ищу дальше"
		    if int(user['response'][0]['city']) == int(cities[choise]['cid']):
			counter = counter+1
			print i+offset, news['response'][i]['text'], user['response'][0]['city']
			print >> htmlFile, '<tr>'
			printTd(counter)
			printTd(news['response'][i]['text'])
			link = 'http://vk.com/id'
			link += str(news['response'][i]['owner_id'])
			printTdHref(link,news['response'][i]['owner_id'])
			print >> htmlFile, '</tr>'
	except (IndexError):
	    print 'Кажется, что-то пошло не так, не могу забрать новость'

    offset = offset+200


print >> htmlFile, '</table>'
htmlFile.close
os.system("open " +reportFile)