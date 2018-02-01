"""

	ash_ffffind.py
	v1.1 (September 14, 2015)
	by me@aaronhildebrandt.com
	
	Automatically downloads all images from ffffound saved by a specific user.
	Will first try to download the image from the original source (to get the highest quality possible).
	If that fails, it'll download the cached version from ffffound.
	
	Prerequisities:
		Beautiful Soup (http://www.crummy.com/software/BeautifulSoup/)
	
	Usage:
		python ffffind.py username

"""



import os, sys, urllib, imghdr
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
from posixpath import basename, dirname

class URLOpener(urllib.FancyURLopener):
	version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

urllib._urlopener = URLOpener()


def main(user):
	offset = 0
	page = 1
	while True:
		print "Capturing page "+str(page)+" ..."
		print
		f = urllib.urlopen("http://ffffound.com/home/"+user+"/found/?offset="+str(offset))
		s = f.read()
		f.close()
		if "<div class=\"description\">" in s:
			images = []
			offset += 25
			count = 0
			soup = BeautifulSoup(s)
			for i in soup.findAll("div", { "class" : "description" }):
				images.append({"url": urlparse("http://" + str(i).split("<br />")[0].replace("<div class=\"description\">", ""))})
			for i in soup.findAll("img"):
				if str(i).find("_m.") != -1:
					images[count]["backup"] = str(i).split("src=\"")[1].split("\"")[0]
					count += 1
			for i in images:
				if os.path.exists(user+"/"+basename(i["url"].path)):
					print basename(i["url"].path) + " exists, stopping."
					print
					sys.exit()
				else:
					print "Downloading " + basename(i["url"].path),
					try:
						urllib.urlretrieve(i["url"].geturl(), user+"/"+basename(i["url"].path))
						print "... done."
						if not imghdr.what(user+"/"+basename(i["url"].path)) in ["gif", "jpeg", "png", None]:
							print "... unfortunately, it seems to be a bad image.\nDownloading backup",
							try:
								urllib.urlretrieve(i["backup"], user+"/"+basename(i["url"].path))
								print "... which seems to have worked."
							except:
								print "... which also failed."
						if os.path.getsize(user+"/"+basename(i["url"].path)) < 5000:
							raise
					except:
						print "... failed. Downloading backup",
						try:
							urllib.urlretrieve(i["backup"], user+"/"+basename(i["url"].path))
							print "... which seems to have worked."
						except:
							print "... which also failed."
				print
			page += 1
		else:
			print "Reached the end of the list, stopping."
			break

if __name__ == '__main__':
	print
	print("ffffound image downloader")
	print
	if len(sys.argv) < 2:
		print "Usage:\n\t python ffffind.py username"
		print
	else:
		try:
			if not os.path.exists("./"+sys.argv[1]):
				os.mkdir(sys.argv[1])
		except:
			print "Error creating directory."
			sys.exit()
		user = sys.argv[1]
		print "Downloading all pictures from user '"+user+"'"
		print
		main(user)