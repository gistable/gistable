import appex, bs4, dialogs, urllib2, webbrowser
if appex.is_running_extension():
	starturl = appex.get_url()
else:
	#ask for video url
	starturl = dialogs.form_dialog(fields=[{'type':'url', 'title':'URL:', 'key':'url'}])['url']
#handle redirects, in case of shortened url
url = urllib2.urlopen(urllib2.Request(starturl)).geturl()
#keepvid page url
url = 'http://www.keepvid.com/?url='+url.split('&feature')[0]
#beautifulsoup object of keepvid page
soup = bs4.BeautifulSoup(urllib2.urlopen(url).read())
#find valid links
links = []
for l in soup.select('a'):
	if l.get('href'):
		if 'googlevideo.com' in l.get('href'):
			links.append(l)
#Open the link
if not appex.is_running_extension():
	webbrowser.open('safari-'+links[0].get('href'))
else:
	print links[0].get('href')