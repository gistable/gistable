#coding:utf-8
#!/usr/bin/python 
import urlparse,urllib,urllib2,os
from bs4 import BeautifulSoup

print "======start======"
print "./dbmeizi"
def downloadImage(imageURL):
	
	url = urlparse.urlparse(imageURL)
	i = len(url.path) - 1
	while i > 0:
		if url.path[i] == '/':
			break
		i = i - 1

	filename = url.path[i+1:len(url.path)]
	urllib.urlretrieve(imageURL,"./dbmeizi/"+filename);

	print filename+"..... done"


def findMM():
	os.makedirs("./dbmeizi")
	index = 0
	while True:
	
		htmlString = urllib2.urlopen("http://www.dbmeizi.com/?p="+str(index)).read()
		soup = BeautifulSoup(htmlString)

		pics = soup.findAll("div",{"class":"pic"})

		if len(pics) == 0:
			return

		for person in pics:
			mz = person.find("img")
			picURL = mz["data-bigimg"]
			downloadImage(picURL)
			#print "==="

		index = index + 1

findMM()

print "======end======"






