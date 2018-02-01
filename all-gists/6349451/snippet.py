# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests

username = '' ###账号###
password = '' ###密码###
login_url = 'http://v2ex.com/signin' ###如V2EX设置了使用 SSL,必须改 https###
index_url = 'http://v2ex.com' ###同上###
mission_url = 'http://www.v2ex.com/mission/daily' ###同上###
UA = "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/27.0.1453.116 Safari/537.36"
headers = {
		"User-Agent": "UA",
		"Host": "v2ex.com",
		"Origin": "http://v2ex.com",
		"Referer": "http://www.v2ex.com/signin"
	}
v2ex_session = requests.Session()

def make_soup(url, tag, name):
	page = get_page(url)
	soup = BeautifulSoup(page)
	what_we_got = soup.find(attrs={tag:name})
	return what_we_got

def get_page(url):
	page = v2ex_session.get(url, headers=headers, verify=False).text
	return page

def mix_post_info(url):
	once_value = make_soup(url, 'name', 'once')['value'].encode('ascii')
	post_info = {
			"next": "/",
			"u": username,
			"p": password,
			"once": once_value,
			"next": "/"
		}
	return post_info

def try_login(url):
	post_info = mix_post_info(url)
	resp = v2ex_session.post(url, data=post_info, headers=headers, verify=False)
	if check_balance(index_url):
		return True
	else:
		return False

def money_link(url):
	short_url = make_soup(url, 'class', 'super normal button')['onclick']
	first_quote = short_url.find("'")
	last_quote = short_url.find("'", first_quote+1)
	short_url = short_url[first_quote+1:last_quote]
	return index_url + short_url

def check_balance(url):
	money_tag = make_soup(url, 'class', 'balance_area')
	if money_tag:
		money = money_tag.contents[0].strip() + money_tag.contents[2].strip()
		return money
	else:
		return None

def check_and_do():
	if try_login(login_url):
		print 'login successfully...'
		print 'current balance: ' + check_balance(index_url)
		mission = make_soup(index_url, 'class', 'icon-gift')
		if mission:
			print 'now take todays money...'
			get_money = money_link(mission_url)
			print 'update balance: ' + check_balance(get_money)
		else:
			print 'already take todays money...'
	else:
		print 'login fail...'

check_and_do()