#!/usr/bin/python2.7
# -*- coding: UTF-8 -*-


"""
This is really weird 
im able to properly 
encode just basic text 
but if it has html tags
i get an encoding error
even though im encoding 
in utf-8

wat???

"""
import requests
import codecs
from bs4 import BeautifulSoup

class File(object):

	''' All This Works ! '''

	def __init__(self, fileName, toWrite=None):
		self.fileName = fileName
		self.toWrite = toWrite

	def read(self):
		f = open(self.fileName, 'r')
		for line in f:
			return (line) 
		f.close()

	def write(self):
		f = codecs.open('test', encoding='utf-8', mode='w')
		f.write(self.toWrite) 
		f.close()


class Site(object):

	''' All this works'''

	def __init__(self, site):
		self.site = site
		self.r = requests.get(self.site)

	def getRaw(self):
		return self.r.content

	def getText(self):
		soup = BeautifulSoup(self.getRaw())
		return soup.get_text()

	def getLinks(self):
		soup = BeautifulSoup(self.getRaw())
		return soup.find_all('a')
		


def download():

	site = 'https://gist.github.com/BurningPixel/63fcf38eb648c30f4d72'
	textF = 'text.txt'

	"""
	site = raw_input('Enter | Site |  > ') 
	saveTo = raw_input('Enter | File |  > ')
	"""



	r = Site(site)
	print (r.getLinks())
	f = File(textF, r.getText())
	f.write()
	print("Done") 


def main():
	download()

if __name__ == '__main__':
	main()	
