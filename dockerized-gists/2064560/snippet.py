import datetime
#import urllib2
import re 
import os
from pyPdf import PdfFileWriter, PdfFileReader
from urllib2 import Request, urlopen
from StringIO import StringIO

#date in the url format
now = datetime.datetime.now()
now = str(now.day) + str(now.month) + str(now.year)
now = '1732012' #the files for 18th is not yet available

#this is the format of the url, its the sixth page of 17-2-2012
sampleurl = 'http://epaper.ekantipur.com/1732012/epaperpdf/1732012-md-hr-6.pdf'

#counting the number of pages available
file = urlopen('http://epaper.ekantipur.com/ktpost/' + now +'/pages.xml')
data = file.read()
pages = []
count = data.count('<page>')
#creating the list of all the pdf urls
for i in range(1,count+1):
  pages.append('http://epaper.ekantipur.com/' + now + '/epaperpdf/' +now +'-md-hr-'+str(i) +'.pdf')

writer = PdfFileWriter()
for i in pages:
	remoteFile = urlopen(Request(i)).read()
	memoryFile = StringIO(remoteFile)
	pdfFile = PdfFileReader(memoryFile)
	for pageNum in xrange(pdfFile.getNumPages()):
		currentPage = pdfFile.getPage(pageNum)
		writer.addPage(currentPage)


outputStream = file("output.pdf","wb")
writer.write(outputStream)
outputStream.close()