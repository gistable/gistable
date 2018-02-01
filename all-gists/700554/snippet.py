#!/usr/bin/python3
# -*- coding: utf-8 -*-
#naruto-link-fetcher.py
#      
#Copyright 2010 Vasudev Kamath <kamathvasudev@gmail.com>
#      
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU  General Public License as published by
#the Free Software Foundation; either version 3 of the License, or
#(at your option) any later version.
#     
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#      
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#MA 02110-1301, USA.
#



import re
import sys
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError


#<iframe.*?src=[\'|\"]http:\/\/.*?url=(http:\/\/.*?\.mp4)[\'|\"].*?></iframe>
# String of interest
# <iframe src="http://95.211.72.7/~animeshi/book.php?config=http://www.animeshippuuden.com/xml.php?url=http://video.ak.fbcdn.net/cfs-ak-snc4/77328/62/149261478453338_1801.mp4" frameborder="0" scrolling="no" width="480" height="412"></iframe>
# Out of this i need only http://video.ak.fbcdn.net/cfs-ak-snc4/77328/62/149261478453338_1801.mp4



url_string = "http://www.animeshippuuden.com/naruto-shippuuden-episode-{}"
pattern = re.compile('<iframe.*?src=[\'|\"]http:\/\/.*?url=(http:\/\/.*?\.mp4)[\'|\"].*?></iframe>')
pattern2 = re.compile('<embed.*?src=[\'|\"]http:\/\/.*?video_src=(http:\/\/.*?\.mp4).*?[\'|\"].*?></embed>')

def get_episode_links(episode):
    global url_string
    try:
        url_string = url_string.format(episode)
        print(("Connecting to {}".format(url_string)))
        request = Request(url=url_string)
        request.add_header("User-Agent","Naruto Link Crawler")
        response = str(urlopen(request).read())
        urls = pattern2.findall(response)
        # if len(urls) == 0:
        #     urls = pattern2.findall(response)
        return urls
    
    except HTTPError as e:
        print(("I got Error code {}".format(e.code)))
    except URLError as u:
        print(("Something went wrong {}".format(u.reason)))
    except:
        print("Unknown Error")

if __name__ == "__main__":
    episode = eval(input("Enter episode number: "))
    if not isinstance(episode,int):
        print("Please enter a valid episode number")
        sys.exit(1)

    urls = get_episode_links(episode)
    if urls:
        print("Got Following URLs")
        i = 1
        for url in urls:
            print(("{}. {}".format(i,url)))
            i += 1

    print("\nPlease choose and download from above links. Enjoy naruto episode :)")
