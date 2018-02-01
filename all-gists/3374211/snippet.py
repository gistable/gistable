# download images from last.fm

# PyQuery is a very powerful module to parse HTML pages, but it is not by default distributed with Python
# if you want install it you need first install lxml module
# Same features of this script works only with pyquery, but the most important ones (download images of cover and artist) works without installing it

try:
	from pyquery import PyQuery as pq
	pyquery = True
except ImportError:
	pyquery = False

# Create an istance of FancyURLopener to avoid to be banned from certains sites that reject no browser user agent

from urllib import FancyURLopener, quote_plus
class MyOpener(FancyURLopener):	
	version = "Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.9.2.4) Gecko/20100513 Firefox/3.6.4"
	
import sys


def openURL(url):
	""" Open a URL using the Firefox user agent to avoid to be banned from getting the page content """
	myopener = MyOpener()
	u = myopener.open(url)
	s = u.read()
	u.close()
	return s
def downloadURL(url, f):
	myopener = MyOpener()
	myopener.retrieve(url, filename = f)

def  decodeArgs(s,encoding = sys.getfilesystemencoding()):
	""" Encode arguments to pass as GET request to lastfm """
	return quote_plus(s.decode(encoding).encode("utf-8"))

	
def findArtistImage_npq(s):
	""" Return a dictionary of art images
	This funtion not use pyquery to parse HTML and it is very rough, improove it if you wish """
	import re
	regex = re.compile('<img[^>]*>')
	images=regex.findall(s)
	img=[i for i in images if i.find("catalogueImage")!=-1]
	regex=re.compile('src\b*=\b*"([^"]*)"')
	try:
		link=regex.findall(img[0])
		return link[0]
	except IndexError: return None

def findAlbumImage_npq(s):
	""" Returns album cover without using pyquery, code it is very rough """
	import re
	try:
		s = s.split('<span id="albumCover" class="albumCover coverMega">')[1].split('</span>')[0]
		regex=re.compile('src\b*=\b*"([^"]*)"')
		img = regex.findall(s)[0]
		return img
	except IndexError: return None

def findArtistImage_pq(s):
	d = pq(s)
	img=d('.resource-images img[itemprop="image"]').eq(0)
	return img.attr("src")

def findAlbumImage_pq(s):
	d=pq(s)
	return d('.g.album-cover-wrapper img').eq(0).attr('src')


	

def getImages(artist, album=None):
	if album: 
		s= openURL(getUrl(artist, album))	
		name="%s - %s" %(prettyName(artist), prettyName(album))
	else: 
		s = openURL(getUrl(artist))
		name=prettyName(artist)
	if pyquery:
		if album:r = findAlbumImage_pq(s)
		else: r = findArtistImage_pq(s)
	else:
		if album:r = findAlbumImage_npq(s)
		else: r = findArtistImage_npq(s)
	# Check for some invalid arguments
	# This part of code needs to be improoved raising exception to distinguish from different type of errors
	if r=="http://cdn.last.fm/flatness/catalogue/noimage/2/default_album_mega.png": r ="Not found"
	return {"url" : r, "name" : name}

def getUrl(artist, album = None):
	url="http://www.lastfm.it/music/"
	url +=decodeArgs(artist)
	if (album): url +="/" + decodeArgs(album)
	return url
	
def prettyName(s):
	return  " ".join(word.capitalize() for word in s.split())

	
if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description="Download artist's and album's images from Last.fm.")
	group = parser.add_mutually_exclusive_group()
	parser.add_argument('artist',
	help="Artist name")
	parser.add_argument("-a","--album", dest="album", default = None,
	help="Album title")
	group.add_argument("-d", "--download", action="store_true",
	help="Download the detected image")
	group.add_argument("-f","--file", 
	help="Name of the downloaded file")
	
	args = parser.parse_args()
	img=getImages(args.artist, args.album)
	print img["url"]
	
	if args.download:
		args.file ="%s.%s" %(img["name"], img["url"].split('.')[-1])
		args.file=args.file.decode(sys.getfilesystemencoding())
	if args.file:
		downloadURL(img["url"], args.file)
		print "Image as been downloaded successfully as %s" %args.file