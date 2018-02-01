#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import urllib, urllib2
import json

MOVIES = {
    'title_prompt': "Search for a movie title (or type 'tv' to switch to TV Shows): ",
    'search_url': "http://ax.itunes.apple.com/WebObjects/MZStoreServices.woa/wa/wsSearch?entity=movie&term=",
    'name_node': 'trackName',
}
TV = {
    'title_prompt': "Search for a TV Show season (or type 'movie' to switch to Movies): ",
    'search_url':  "http://ax.itunes.apple.com/WebObjects/MZStoreServices.woa/wa/wsSearch?entity=tvSeason&term=",
    'name_node': 'collectionName',
}

media = MOVIES

SAVE_TO = "%s/Desktop/" % os.environ["HOME"] # Directory must exist
TITLES = [] # Optionally populate this with a list of titles for batch processing

def get_art(title=None, keep_going=False):
    global not_found, media
    if not title:
        title = raw_input(media['title_prompt'])
        if title == "movie":
            media = MOVIES
            get_art(None, True)
        elif title == "tv":
            media = TV
            get_art(None, True)
        elif title == "exit":
            exit();
    
    print "\nSearching for \"%s\"..." % title
    
    search_term = urllib.quote_plus(title)

    try:
        response = urllib2.urlopen("%s%s" % (media['search_url'], search_term))
        results = json.load(response)
        resultCount = results['resultCount']
        if resultCount > 0:
            if resultCount == 1:
                which = 0
            else:
                for index, result in enumerate(results['results']):
                    print "%s. %s" % (index+1, result[media['name_node']])
                which = raw_input("\nEnter a number to download its artwork (or hit Enter to search again): ")
                try:
                    which = int(which) - 1
                except:
                    which = None
                    not_found.append(title)
            if which != None:
                url = results['results'][which]['artworkUrl100'].replace("100x100-75.", "")
                sys.stdout.write("Downloading artwork...") 
                urllib.urlretrieve(url, "%s%s.jpg" % (SAVE_TO, title.replace("/", "-").replace(":", " -")))
                sys.stdout.write(" done.\n\n")
            
        else:
            print "No results found for \"%s\"" % title
            not_found.append(title)
    except urllib2.HTTPError:
        not_found.append(title)
        pass
    
    if keep_going:
        get_art(None, True)

if __name__ == "__main__":
    not_found = []
    if TITLES:
        for title in TITLES:
            get_art(title)
    else:
        get_art(None, True)
    print "\n\nArtwork was not found for the following titles:"
    for title in not_found:
        print title
