#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# Usage: ./tmdb_scrape.py <movie title>
#
# A scraper à la MediaElch for XBMC.
#
# Searches for the given movie, retrieves the movie information from TMDb (only
# user ratings are retrieved from IMDb) and saves it to the .nfo file.
# Additionally a movie poster (best rated), a backdrop (also best rated) and
# thumbnails for actors are downloaded to the working dir.
#
# Requirements
#
# lxml
# pytmdb3
# imdbpy

import sys

# Import the tmdb package.
try:
    from tmdb3 import set_key, searchMovie
except ImportError:
    print 'You need to install the pytmdb3 package!'
    sys.exit(1)

if len(sys.argv) != 2:
    print 'Only one argument is required:'
    print '  %s "movie title"' % sys.argv[0]
    sys.exit(2)

# This key is taken from the XBMC TMDb scraper
set_key('57983e31fb435df4df77afb854740ea9')

in_encoding = sys.stdin.encoding or sys.getdefaultencoding()
out_encoding = sys.stdout.encoding or sys.getdefaultencoding()

title = unicode(sys.argv[1], in_encoding, 'replace')

print "Retrieving movie \"%s\" from TMDb" % title 

res = searchMovie(title)
if len(res) == 0:
	print "\"%s\" not found. Try a different one." % title
	sys.exit(0)

m = res[0]

print "Retrieving additional information from IMDb"

# Import the tmdb package.
try:
    import imdb
except ImportError:
    print 'You need to install the imdbpy package!'
    sys.exit(1)

i = imdb.IMDb()
m_imdb = i.get_movie(m.imdb[2:], ['main'])

#
# print nfo
#

from lxml.builder import E
from lxml import etree

# sort posters by user rating
posters = sorted(m.posters, key=lambda x: -x.userrating)
backdrops = sorted(m.backdrops, key=lambda x: -x.userrating)

nfo = (
	E.movie(
		E.title(m.title),
		E.original_title(m.originaltitle),
		E.rating(str(m_imdb['rating'])),
		E.votes(str(m_imdb['votes'])),
		E.top250("0"), 
		E.year(str(m.releasedate.year)),
		E.plot(m.overview),
		E.tagline(m.tagline),
		E.runtime(str(m.runtime)),
		E.mpaa(m_imdb['mpaa']),
		E.credits(', '.join([x.name for x in m.crew if x.job == 'Screenplay'])),
		E.director(', '.join([x.name for x in m.crew if x.job == 'Director'])),
		E.playcount('0'),
		E.id(m.imdb),
		E.tmdbid(str(m.id)),
		E.trailer(m.youtube_trailers[0].geturl() if len(m.youtube_trailers) else ""),
		E.watched('false')
	)
)

for x in m.studios:
	nfo.append(E.studio(x.name))
for x in m.genres:
	nfo.append(E.genre(x.name))
for x in m.countries:
	nfo.append(E.country(x.name))
for x in m.cast[0:10]:
	nfo.append(
		E.actor(
			E.name(x.name),
			E.role(x.character),
			E.thumb(x.profiles[0].geturl() if len(x.profiles) else "")
		)
	)

# poster previews
for p in posters[0:10]:
	if 'w342' in p.sizes():
		nfo.append(E.thumb(p.geturl('w342'), preview=p.geturl('w342')))

# fanart previews
fanart = E.fanart()
for b in backdrops[0:6]:
	if 'w780' in b.sizes():
		fanart.append(E.thumb(b.geturl('w780'), preview=b.geturl('w780')))
nfo.append(fanart)

# TODO: Fileinfo

print "Writing nfo"
with open(title + '.nfo', 'w') as f:
	f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
	f.write(etree.tostring(nfo, pretty_print=True))
	f.close()

#
# Build download list for poster, fanart and actors
#

downloads = []

poster_url = posters[0].geturl()
poster_filename = "%s-poster.%s" % (title, poster_url.split('.')[-1])
downloads.append((poster_filename, poster_url))

fanart_url = backdrops[0].geturl()
fanart_filename = "%s-fanart.%s" % (title, fanart_url.split('.')[-1])
downloads.append((fanart_filename, fanart_url))

for a in m.cast[0:10]:
	if a.profile:
		url = a.profile.geturl(a.profile.sizes()[-2])
		filename = '.actors/%s.%s' % (a.name.replace(' ', '_'), url.split('.')[-1])
		downloads.append((filename, url))

#
# Download files
#

import os, urllib2

try:
	os.mkdir('.actors')
except Exception, e:
	pass

for filename, url in downloads:
	u = urllib2.urlopen(url)
	f = open(filename, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	print "Downloading: %s Bytes: %s" % (filename, file_size)

	file_size_dl = 0
	block_sz = 8192
	while True:
	    buffer = u.read(block_sz)
	    if not buffer:
	        break

	    file_size_dl += len(buffer)
	    f.write(buffer)

	f.close()