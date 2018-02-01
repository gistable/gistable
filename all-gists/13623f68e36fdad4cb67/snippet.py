#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Work with cookies was done by n8henrie
# https://gist.github.com/n8henrie/8715089

import sqlite3
import urllib.parse
import keyring
import requests

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

import re, os, sys
import urllib.request

from subprocess import Popen
from shutil import copyfile

# Скрипт для тех, кто не просматривает темы в поиске чего-бы скачать, я сначала скачивает, чтобы потом перебрать скачанное в поиске интересного.
# Чтобы торренты не повторялись, можно в ветках форума кликнуть по "Опции показа" и отметить "только новые темы".

#!!!!!!!!!!!
# Для тех кто пользуется подобным методом - имейте совесть, и отдавайте скачанное до рейтинга 1x
#!!!!!!!!!!!

# Подходит только для линукса; по ссылке в самом начале автор работы с куками имеет метод для Эппл-ос.
# Игнорирует темы которые записаны в историю хрома.
# Останавливается когда достигнут лимит скачиваний в сутки и выдает сообщение.
# Останавливается если истекла куки-сессия и выдает ошибку.
# После обновления сессии на порнолабе, хрому требуется некоторое время чтобы обновить базу куков(=<1мин).

# Нельзя подключиться к бд истории хрома пока он работает, поэтому копирую историю в /tmp; по этой же причине не стал насильно вживлять ссылки на скачанные торренты в базу хрома.
# Ссылки на скачанные темы пишет в 2 файла, первый для файлов до N Гб, второй больше.
# После скачивания открывает оба файла в хроме, если в них записаны новые темы, чтобы можно было их открыть для записи в историю хрома (плагин Linkclump для открытия N ссылок простыней).

#########################

# количество страниц в форумах из которых выдирать торренты, если скрипт стоит в кроне, то больше одной не понадобится
urls_pages = 1

# ссылки на форумы с которых собирать темы
urls = """
	http://pornolab.net/forum/viewforum.php?f=1671
	http://pornolab.net/forum/viewforum.php?f=1726
	http://pornolab.net/forum/viewforum.php?f=883
	http://pornolab.net/forum/viewforum.php?f=1296
"""

# пропускать темы в которых есть слова (1 слово на строку; регистр не важен)
block_words = """
	240p
	320p
	480p
	540p
	Foxycombat
	Danni.com
"""

# ссылки на торренты с размером больше N Гб будут записаны во второй файл
# в данном случае сам торрент-файл не будет скачан
limit_gb = 3

file_w_links = os.path.expanduser('~/Downloads/pornolab_urls.htm')
file_w_links_big = os.path.expanduser('~/Downloads/pornolab_urls_2_big.htm')

########################

def chrome_cookies(url):
	
	salt = b'saltysalt'
	iv = b' ' * 16
	length = 16	
		
	def chrome_decrypt(encrypted_value, key=None):
		
		# Encrypted cookies should be prefixed with 'v10' according to the 
		# Chromium code. Strip it off.
		encrypted_value = encrypted_value[3:]
 
		# Strip padding by taking off number indicated by padding
		# eg if last is '\x0e' then ord('\x0e') == 14, so take off 14.
		# You'll need to change this function to use ord() for python2.
		def clean(x):
			return x[:-x[-1]].decode('utf8')
 
		cipher = AES.new(key, AES.MODE_CBC, IV=iv)
		decrypted = cipher.decrypt(encrypted_value)
 
		return clean(decrypted)
			
	my_pass = 'peanuts'.encode('utf8')
	iterations = 1
	cookie_file = os.path.expanduser('~/.config/chromium/Default/Cookies')

	# Generate key from values above
	key = PBKDF2(my_pass, salt, length, iterations)
	
	# Part of the domain name that will help the sqlite3 query pick it from the Chrome cookies
	domain = urllib.parse.urlparse(url).netloc
 
	conn = sqlite3.connect(cookie_file)
	sql = 'select name, value, encrypted_value from cookies '\
			'where host_key like "%{}%"'.format(domain)
 
	cookies = {}
	cookies_list = []
	
	with conn:
		for k, v, ev in conn.execute(sql):
			
			# if there is a not encrypted value or if the encrypted value
			# doesn't start with the 'v10' prefix, return v
			if v or (ev[:3] != b'v10'):
				cookies_list.append((k, v))
			else:
				decrypted_tuple = (k, chrome_decrypt(ev, key=key))
				cookies_list.append(decrypted_tuple)
		cookies.update(cookies_list)
	
	return cookies


cooks = chrome_cookies('http://pornolab.net/')
try:
	CC = 'opt_js=' + cooks['opt_js'] + '; bb_data=' + cooks['bb_data'] + '; bb_t=' + cooks['bb_t'] + ';'
except:
	os.system('notify-send "Pornlab" "No Cookies!"')
	sys.exit('No Cookies! - Sign In - http://pornolab.net/')

urls = [ x.strip() for x in urls.split('\n') if len(x.strip()) != 0 ]
urls2 = []
topics = []

block_words = [ x.strip().lower() for x in block_words.split('\n') if len(x.strip()) != 0 ]

for ui in urls:
	for ppop in range(0, urls_pages*50, 50):
		urls2.append(ui + '&start=' + str(ppop))

for ui in urls2:
	print(ui)
	req = urllib.request.Request(ui)
	req.add_header('Cookie', CC)
	r = urllib.request.urlopen(req).read().decode('windows-1251')
	
	topics = topics + re.findall('class="torTopic bold tt-text">(.*?)</a>.*?<a href="dl\.php\?t=(.*?)" class="small f-dl dl-stub" style="text-decoration: none">(.*?)</a>', r, re.DOTALL)
	
if len(topics) == 0:
	os.system('notify-send "Pornlab" "Faulty Cookies!"')
	sys.exit('Faulty Cookies! - http://pornolab.net/')

copyfile(os.path.expanduser('~/.config/chromium/Default/History'), '/tmp/chromium_History')
conn = sqlite3.connect('/tmp/chromium_History').cursor()

ff1 = 0
ff2	= 0

for tp in topics:
	name, topic, size = tp
	
	# if topic name has block word
	for bwd in block_words:
		if bwd in name.lower():
			print(topic + ' has block word')
			continue
	
	conn.execute('SELECT count() FROM urls WHERE url="http://pornolab.net/forum/viewtopic.php?t=' + topic + '";')
	
	# if topic is new
	if conn.fetchone()[0] == 0:
		size = size.split('&nbsp;')
		
		if size[1] == 'GB' and float(size[0]) > limit_gb:
			open(file_w_links_big, 'a').write('<a href="http://pornolab.net/forum/viewtopic.php?t=' + topic + '">http://pornolab.net/forum/viewtopic.php?t=' + topic + '</a> - ' + tp[2] + '<br>\n')
			
			ff2 += 1
			continue
		
		ff1 += 1
		print(topic)
		
		req = urllib.request.Request('http://pornolab.net/forum/dl.php?t=' + topic)
		req.add_header('Cookie', CC + 'bb_dl=' + topic)
		
		r = urllib.request.urlopen(req).read()
		
		# die if limit was reached
		try:
			if 'Вы уже исчерпали суточный лимит скачиваний торрент-файлов' in r.decode('windows-1251'):
				Popen('banner -f 2 limit was reached', shell=True)
				break
		except:
			pass
		
		open(os.path.expanduser('~/Downloads/') + topic + '.torrent', 'wb').write(r)
		
		open(file_w_links, 'a').write('<a href="http://pornolab.net/forum/viewtopic.php?t=' + topic + '">http://pornolab.net/forum/viewtopic.php?t=' + topic + '</a> - ' + tp[2] + '<br>\n')
	else:
		print(topic + ' in history')

Popen('banner -f 2 ' + str(ff1) + ' ' + str(ff2), shell=True)

if ff1:
	os.system('chromium ' + file_w_links)

if ff2:
	os.system('chromium ' + file_w_links_big)
