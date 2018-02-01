#coding: utf-8
from urllib import quote
import json
import re
import sys
import webbrowser
import requests
import htmlentitydefs

movie = quote(sys.argv[1])

## Unescape function from: http://effbot.org/zone/re-sub.htm#unescape-html
def unescape(text):
	def fixup(m):
		text = m.group(0)
		if text[:2] == "&#":
			# character reference
			try:
				if text[:3] == "&#x":
					return unichr(int(text[3:-1], 16))
				else:
					return unichr(int(text[2:-1]))
			except ValueError:
				pass
		else:
			# named entity
			try:
				text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
			except KeyError:
				pass
		return text # leave as is
	return re.sub("&#?\w+;", fixup, text)

r = requests.get('http://www.imdb.com/xml/find?json=1&nr=1&tt=on&q=%s' % movie).text
t = json.loads(r)

try:
	pop = t['title_popular'] + t['title_exact']
except:
	try:
		pop = t['title_popular']
	except:
		pop = t['title_exact']

films = {}
for film in pop:
	title = unescape(film['title']).encode('utf_8')
	description = re.match("(^\d{4}).*<a href='/name/nm\d+/'>(.*)</a>", film['description'])
	if description:
		year = description.group(1)
		director = unescape(description.group(2)).encode('utf_8')
		the_string = '%s (%s, %s)' % (title, year, director)
		films[the_string] = {'Title': title, 'Year': year, 'Director': director}
	
if len(films.keys()) == 1:
	for film in films.keys():
		dayone = """dayone://post?entry={{{{|{0}||
|:---:|---:|
|{1}|{2}""".format(films[film]['Title'], films[film]['Director'],films[film]['Year'])
	dayone+="""|
|[list:What's the rating?|★ ★ ★ ★ ★|★ ★ ★ ★|★ ★ ★|★ ★|★]||

#Movies}}"""
else:
	dayone = 'dayone://post?entry=[[list:What\'s the movie?'
	for film in films.keys():
		dayone+="""|{0}=%7C{1}%7C%7C%0A%7C%3A---%3A%7C---%3A%7C%0A%7C{2}%7C{3}""".format(film, quote(films[film]['Title']), quote(films[film]['Director']), films[film]['Year'])
	dayone+="]]"
	dayone+="""{{|
|[list:What's the rating?|★ ★ ★ ★ ★|★ ★ ★ ★|★ ★ ★|★ ★|★]||

#Movies}}"""

the_url = 'launchpro://?url=' + quote(dayone)
webbrowser.open(the_url)