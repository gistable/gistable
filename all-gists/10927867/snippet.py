#!/usr/bin/env python
import sys
import plistlib
import urllib2
import re

GENRE_LINE = '<a href="http://www.blogger.com/wiki/Music_genre" title="Music genre">Genres</a>\n'
URL_PREFIX = 'http://en.wikipedia.org/wiki/Special:Search/'

artist_genre = {}
unknown_genre = []

def parse_genre(artist):
    genres = ''
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    url = ''.join([URL_PREFIX, artist])
    print 'Searching:', url
    try:
        infile = opener.open(url)
        page = infile.readlines()

        startindex = page.index(GENRE_LINE)
        line = None
        while line != '\n':
            startindex += 1
            line = page[startindex]
            genre = re.sub('&lt;.*?&gt;', '', line.strip())
            if len(genre) &gt; 0:
                genres += genre.lower() + ', '

        if genres.endswith(', '):
            genres = genres[:-2]

    except Exception, e:
        pass
    return genres

def usage(name):
    print '%s "iTunes Music Library.xml"' % name

def main(argv=sys.argv):
    if len(argv) &gt; 1:
        plist = argv[1]
    else:
        usage(argv[0])
        sys.exit(0)

    pl = plistlib.readPlist(plist)
    for trackid in pl['Tracks'].keys():
        if pl['Tracks'][trackid].has_key('Artist'):
            artist = pl['Tracks'][trackid]['Artist']

            if artist not in unknown_genre:

                if artist_genre.has_key(artist):
                    pl['Tracks'][trackid]['Genre'] = artist_genre[artist]
                else:
                    wiki_artist = re.sub(' ', '_', artist)
                    wiki_genre = parse_genre(wiki_artist)

                    # didn't find the genre the first time, try appending _(band) to the artist name
                    # and try again
                    if wiki_genre == '':
                        wiki_artist = ''.join([wiki_artist, '_(band)'])
                        wiki_genre = parse_genre(wiki_artist)

                        # still nothing, no genres found for this artist
                        if wiki_genre == '':
                            unknown_genre.append(artist)
                            print 'Couldn\'t find genre for', artist
                        else:
                            found_genre = True
                    else:
                        found_genre = True

                    if found_genre:
                        artist_genre[artist] = wiki_genre
                        pl['Tracks'][trackid]['Genre'] = wiki_genre
                        print '%s is labeled as %s' % (artist, wiki_genre)

    plistlib.writePlist(pl, ''.join(['NEW.', plist]))

    print '####################################################'
    print '# Could not find genres for the following artists: #'
    print '####################################################'
    for i in unknown_genre:
        print i

if __name__ == '__main__':
    main()