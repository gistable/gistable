#!/usr/bin/python

from urlgrab import Cache
from BeautifulSoup import MinimalSoup as BeautifulSoup
from re import compile
from os.path import exists, getsize, dirname, join
from urllib import urlretrieve, urlencode, quote
from sys import argv
import demjson
import zlib

folder = dirname(argv[0])

cache = Cache(debug=False)

pages = []

for index in range(1,11):
        index = cache.get("http://www.escapistmagazine.com/videos/view/zero-punctuation?page=%d"%index, max_age=60*60*2).read()
        index = index.replace("''>","'>")
        index = BeautifulSoup(index)

        for link in index.findAll("a"):
                if not link.has_key("href"):
                        continue
                if link["href"].find("http://www.escapistmagazine.com/videos/view/zero-punctuation/")!=-1:
                        short_href = link["href"]
                        slash = short_href.rfind("/")
                        if short_href[slash:].find("-")!=-1:
                                short_href = short_href[slash+1:slash+short_href[slash:].find("-")]
                        else:
                                short_href = short_href[slash+1:]

                        assert len(short_href)>0, link["href"]

                        if short_href not in pages:
                                pages.append(short_href)
        break

js = compile("imsVideo.play\((\{[^}]+\})")
mp4 = compile("'url':'(http://video2?.(?:themis-media|escapistmagazine).com/(?:links/)?[\da-f]+/mp4/escapist/zero-punctuation/[\da-f]+.mp4)'")
desc = compile("'description':\"([^\"]+)\"")

foundold = False

def decoder(e, s):
        t = ""
        a = ""
        r = ""
        while len(t) < len(s)/ 2:
                t += e
        t = t[:len(s) / 2]
        for o in range(0, len(s), 2):
                a += chr(int("" + s[o] + s[o + 1], 16))
        for o in range(len(t)):
                r += chr(ord(t[o]) ^ ord(a[o]))
        return r

print len(pages)
for p in pages:
        page = cache.get("http://www.escapistmagazine.com/videos/embed/"+p, max_age=-1).read()
        try:
                config = js.search(page).groups()
                #print config
                config = demjson.decode(config[0])
                #print config
                url ="http://www.escapistmagazine.com/videos/vidconfig.php?" + urlencode(config)
                encoded = cache.get(url, max_age=-1).read()
        except AttributeError:
                print p
                print page
                raise
        try:
                data = decoder(config["hash"], encoded)
                data = demjson.decode(data)
                #print data
                video = None
                for item in data["files"]["videos"]:
                        if item["type"] == "video/mp4":
                                video = item["src"]
                title = data["videoData"]["title"]
        except AttributeError:
                print config
                raise
        print p, title, video
        fname = "%s.mp4"%title
        fname = fname.replace("&#039;", "'")
        fname = fname.replace("&amp;", "&")
        fname = fname.replace("&gt;", ">")
        fname = fname.replace("&lt;", "<")
        fname = fname.replace("<i>", "")
        fname = fname.replace("</i>", "")
        assert fname.find("&#")==-1,fname
        fname = join(folder, fname)
        if not exists(fname):
                urlretrieve(video, fname)
                assert exists(fname)
                assert getsize(fname)>1000
        else:
                foundold = True

assert foundold, "First page doesn't have one's we've already got. Write the generator code..."