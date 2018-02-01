import feedparser, webbrowser
from datetime import datetime

def uploadToFlipboard( int_day , feed_url ):
	
	date = datetime.today().timetuple()[2]

	d = feedparser.parse(feed_ulr)
	d["feed"]["title"]

	for n in d["entries"]:
    
	if date == n["published_parsed"][2]:
      
		title = n["title"]
		url = n["links"][0]["href"]
        
      		webbrowser.open_new('https://share.flipboard.com/flipit/load?v=1.0&url='+url+'&title='+title)