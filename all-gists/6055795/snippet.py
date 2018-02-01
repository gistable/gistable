#!/usr/bin/python
#coding:utf-8
'''
@author：Byron
新浪微博：http://weibo.com/ziyuetk
'''
import urllib2, json
from city import city

yourcity = raw_input("你想查那个城市的天气？")

#测试yourcity变量是否可以返回你想要的值
#print yourcity

url = "http://www.weather.com.cn/data/cityinfo/" + city[yourcity] + ".html"

#print url #同上

response = urllib2.urlopen(url, timeout=10)
city_dict = response.read()

#此处打印出来是一个json格式的东西
#print city_dict

#用Python的json库来解析获取到的网页json内容
jsondata = json.JSONDecoder().decode(city_dict)

#定义几个变量用来储存解析出来的内容
temp_low = jsondata['weatherinfo']['temp1']
temp_high = jsondata['weatherinfo']['temp2']
weather = jsondata['weatherinfo']['weather']

print yourcity
print weather
print temp_low + "~" + temp_high