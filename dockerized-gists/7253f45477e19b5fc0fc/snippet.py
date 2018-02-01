#!/usr/bin/env python2
# This file is released as public domain by Steven Smith (blha303) in Apr 2015
# In areas where public domain isn't a thing, I release it under the MIT license.
# Although credit would be nice if you use this in something cool. And email me a link too pls.
import time,os,requests,json,subprocess
from urllib import urlretrieve

DTFORMAT = "%a, %b %d %Y %H:%M:%S +0000" # Do not modify, needs to be at top

playlisturl = "https://www.youtube.com/playlist?list=UU9CuvdOVfMPvKCiwdGKL3cQ"
number_to_get = 30
# generate your key via google's api dashboard. needs to have access to youtube's data api v3
apikey = ""
webroot = "http://domain.bla"
webpath = "/var/www"
outpdir = "/podcastdir"
outpfn  = "/{id}.m4a"
xmlfn = outpdir + "/podcast.xml"

podcast = dict(
  self = webroot + xmlfn, # should point to xml
  title = "A cool podcast",
  link = "http://blha303.com.au",
  description = "DAE podcast?",
  copyright = "Copyright 2015 Youtube",
  now = time.strftime(DTFORMAT),
  language = "en-us",
  subtitle = "Youtube is pretty cool, ey",
  author = "Me",
  summary = "Wip wap wop",
  owner_name = "Me",
  owner_email = "me@you.us",
  image = webroot + outpdir + "/podcast.png",
  category = "yay",
  explicit = "yes" # or no
)

item_info = dict(
  author = "Me",
  summary = "Just more info",
  category = "Blablabla",
  keywords = "autogen"
)

BASE = u"""<?xml version="1.0" encoding="utf-8"?>
 <rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
 <channel>
 <atom:link href="{self}" rel="self" type="application/rss+xml" />
     <title>{title}</title>
     <link>{link}</link>
     <description>{description}</description>
     <lastBuildDate>{now}</lastBuildDate>
     <language>{language}</language>
     <copyright>{copyright}</copyright>
     <itunes:subtitle>{subtitle}</itunes:subtitle>
     <itunes:author>{author}</itunes:author>
     <itunes:summary>{summary}</itunes:summary>
     <itunes:owner>
         <itunes:name>{owner_name}</itunes:name>
         <itunes:email>{owner_email}</itunes:email>
     </itunes:owner>
     <itunes:image href="{image}" />
     <itunes:category text="{category}" />
     """
BASE2 = u"""<itunes:explicit>{explicit}</itunes:explicit>
 </channel>
 </rss>
"""
ITEM = u"""<item>
         <title>{fulltitle}</title>
         <link>https://www.youtube.com/watch?v={id}</link>
         <itunes:author>{author}</itunes:author>
         <description>{description}</description>
         <itunes:summary>{summary}</itunes:summary>
         <enclosure url="{lurl}" length="{size}" type="video/mp4"/>
         <guid>{lurl}</guid>
         <pubDate>{upload_date}</pubDate>
         <itunes:order>{order}</itunes:order>
         <itunes:duration>{duration}</itunes:duration>
         <itunes:keywords>{keywords}</itunes:keywords>
         <category>{category}</category>
         <itunes:explicit>{explicit}</itunes:explicit>
     </item>
     """

def get_time(id):
    data = requests.get("https://www.googleapis.com/youtube/v3/videos", params={'id': id, 'part': "snippet,statistics,recordingDetails", "key": apikey}).json()
    return time.strftime(DTFORMAT, time.strptime(data["items"][0]["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%S.000Z"))

def download_file(item):
    fn = webpath + outpdir + outpfn.format(**item)
    if not os.path.isfile(fn):
        print " Downloading"
        url = [i for i in item["formats"] if i["format_id"] == "nondash-140"][0]["url"]
        print "".join(subprocess.check_output(["/usr/bin/wget", url, "-O", fn, "-nv"]).splitlines())
        return fn
    else:
        print " File exists"
        return fn

def get_output(items):
    outp = []
    items = sorted(items, key=lambda k: k["upload_date"], reverse=True)
    for x,item in enumerate(items):
        item.update(item_info)
        print "Processing {fulltitle} ({id})".format(**item)
        m,s = divmod(item["duration"], 60)
        h,m = divmod(m, 60)
        item["order"] = x+1
        item["description"] = item["description"].replace(u"\u25ba", u"&gt;")
        item["duration"] = u"%d:%02d:%02d" % (h,m,s)
        item["upload_date"] = get_time(item["id"])
        item["size"] = str(os.path.getsize(download_file(item)))
        item["explicit"] = podcast["explicit"]
        item["lurl"] = webroot + outpdir + outpfn.format(**item)
        outp.append(ITEM.format(**item))
        print " Processed"
    print "Process complete"
    return BASE.format(**podcast) + "".join(outp) + BASE2.format(**podcast)

if __name__ == "__main__":
    print "Getting playlist data from youtube, this can take a while if the playlist is large..."
    data = subprocess.check_output(['/usr/local/bin/youtube-dl', playlisturl, '--playlist-end', str(number_to_get), '--match-filter', 'duration > 300', '-f', '140', '-j']).splitlines()
    print "Playlist data obtained, starting processing..."
    with open(webpath + xmlfn, "w") as f:
        f.write(get_output(json.loads(u"[" + u",".join(data) + u"]")).encode('ascii', 'ignore'))
