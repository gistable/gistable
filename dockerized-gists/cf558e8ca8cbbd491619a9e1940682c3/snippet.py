import pycurl
import json
import time
from StringIO import StringIO

i = 0
bnums = []

while True :
	print(str(i))
	buffer = StringIO()
	c = pycurl.Curl()
	c.setopt(c.WRITEDATA, buffer)
	c.setopt(c.ENCODING, 'gzip,deflate')
	c.setopt(pycurl.HTTPHEADER, ['Pragma: no-cache',
		'Accept-Language: en-US,en;q=0.8,it;q=0.6',
		'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
		'Accept: text/javascript, text/html, application/xml, text/xml, */*',
		'X-Prototype-Version: 1.7.3',
		'X-Requested-With: XMLHttpRequest',
		'Cookie: PHPSESSID=brfmu8t0mopjk7l96gooerm9b3; bzc=8jdes06rltfc; pwr_new_tooltip=true; bzu=r8desr59d4ds; pwr_selc_auctid=false',
		'Connection: keep-alive',
		'If-Modified-Since: Thu, 1 Jan 1970 00:00:00 GMT',
		'Referer: http://www.beezid.com/{AUCTION_TITLE}',
		'Cache-Control: no-cache'
		])
	c.setopt(c.URL, 'http://www.beezid.com/auctions/updater/id:{AUCTION_ID}/bid:'+str(i))
	c.perform()
	c.close()
	js = buffer.getvalue()
	try:
		jl = json.loads(js)
		if len(jl['bids']) > 0:
			for bid in jl['bids']:
				if bid['id'] > i:
					i = bid['id']
				if any(str(bid['id']) in s for s in bnums):
					pass
				else:
					bnums.append(str(bid['id']))
					with open("log.txt", "a") as myfile:
					    myfile.write(json.dumps(bid))
					    myfile.write("\n")
	except:
		pass
	time.sleep(.5)