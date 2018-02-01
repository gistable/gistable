import urllib2, re, json, os, time, sys, HTMLParser

html_parser = HTMLParser.HTMLParser()

auth_address = "1KbV1e1u6P6AsY8XNBydgtbtN8iSB5WMyG"
auth_privatekey = "xxxx"
site = "1TaLkFrMwvbNsooF4ioKAY9EuxTBTjipT"
zeronet_dir = ".."

os.chdir(zeronet_dir)
json_path = "data/%s/data/users/%s/data.json" % (site, auth_address)

data = json.load(open(json_path))

def addNews(title, source, url, descr):
	global data
	added_urls = [re.match(".*?(http[s]{0,1}://.*$|$)", topic["body"], re.DOTALL).group(1) for topic in data["topic"]]
	added_bodys = [topic["body"] for topic in data["topic"]]
	added_titles = [topic["title"] for topic in data["topic"]]
	if url not in added_urls and descr[0:30] not in "".join(added_bodys) and title[0:30] not in "".join(added_titles):
		topic = {
			"topic_id": data["next_topic_id"],
			"title": title,
			"body": descr+"\n\n"+url,
			"added": int(time.time()),
			"parent_topic_uri": "1_1KbV1e1u6P6AsY8XNBydgtbtN8iSB5WMyG"
		}
		data["next_topic_id"] += 1
		data["topic"].append(topic)
		data["topic"] = [topic for topic in data["topic"] if topic["added"] > time.time()-60*60*24*2 or "type" in topic] # Only keep last 2 day topics + the group
		print "Added:", repr(title)
		return True
	else:
		return False



def getNews():
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11')]
	response = opener.open("https://www.google.hu/search?q=bitcoin+OR+p2p+OR+tor+OR+i2p+OR+decentralized+OR+darkweb+OR+bittorrent+OR+blockchain+OR+namecoin+OR+(p2p+web)&lr=lang_en&safe=images&hl=hu&tbs=qdr:d,lr:lang_1en&source=lnms&tbm=nws&sa=X", timeout=10)
	added = 0
	found = 0

	blocks = re.findall('<div class="g">(.*?)</table>', response.read())
	if not blocks:
		print "No blocks"
	for block in blocks:
		match = re.match('.*?<h3.*? href=\"(?P<url>.*?)\".*?>(?P<title>.*?)</a>.*<div class="slp"><span.*?>(?P<source>[A-Za-z0-9 ]*).*<div class="st">(?P<descr>.*?)</div>(.*?)</td>', block.replace("<b>", "").replace("</b>", ""))
		if match:
			found += 1
			url, title, source, descr, more = match.groups()
			title = html_parser.unescape(title.decode("utf8"))
			descr = html_parser.unescape(descr.decode("utf8"))
			more = more.strip()
			url = re.sub(".*?q=(.*?)&amp;.*", "\\1", url)
			if not more:
				added += addNews(title, source, url, descr)
	if not found:
		print "Not found any"

	if added:
		json.dump(data, open(json_path, "w"), indent=2)
		print "* Sign and publish..."
		os.system("python zeronet.py siteSign %s %s --inner_path data/users/%s/content.json --publish" % (site, auth_privatekey, auth_address))

while 1:
	try:
		getNews()
	except Exception, err:
		print "Exception", err
	print ".",
	sys.stdout.flush()
	time.sleep(60) 
