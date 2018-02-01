#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
slideshare-dl.py
~~~~~~~~~~~~~~~~

slideshare-dl is a small command-line program 
for downloading slides from SlideShare.net

"""

import os
import re
import urllib2

from BeautifulSoup import BeautifulSoup
from xml.etree import ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

import win32com.client #Only Windows for generating ppt
from PIL import Image

class SlideShare(object):
	"""SlideShare download script"""
	def __init__(self, url=None):
		self.url = url
		self.__xml_file = ''
		self.__slide_name = ''
		self.__files = []
		self.__images = []

	def set_xml_file(self):
		url = urllib2.urlopen(self.url)
		source = url.read()

		soup = BeautifulSoup(source)
		html = soup.find("script", {"id": "page-json"})
		
		slide_regex = re.search('"doc":"(.*?)"', str(html), re.IGNORECASE)
		self.__slide_name = str(slide_regex.group(1))
		self.__xml_file = "http://s3.amazonaws.com/slideshare/" + self.__slide_name + ".xml"

	def create_directory(self, dir_name):
		if not os.path.exists(dir_name):
			os.makedirs(dir_name)
		os.chdir(dir_name)

	def files_from(self, xml_file):
		files = []
		try:
			url = urllib2.urlopen(xml_file)
			tree = ET.parse(url)
			element = tree.getroot()

			for subelement in element:
				files.append(str(subelement.get('Src')))
			return files
		except Exception, inst:
			print "Unexpected error opening xml file"

	def download_file(self, url):
		file_name = url.split('/')[-1]
		u = urllib2.urlopen(url)
		f = open(file_name, 'wb')
		meta = u.info()
		file_size = int(meta.getheaders("Content-Length")[0])
		print "Downloading: %s Bytes: %s" % (file_name, file_size)

		file_size_dl = 0
		block_sz = 8192
		while True:
			buffer = u.read(block_sz)
			if not buffer:
				break
			
			file_size_dl += len(buffer)
			f.write(buffer)
			status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
			status = status + chr(8)*(len(status)+1)
			print status,
		f.close()
		self.__files.append(file_name)

	def download(self):
		for url in self.files_from(self.__xml_file):
			self.download_file(url)
		
	def convert_to_images(self):
		for filename in self.__files:
			#swfrender path/to/my.swf -X<width of output> -Y<height of output> -o<filename of output png>
			swfrender_cmd = 'swfrender ' + os.getcwd() + '/' + filename + ' -o ' + os.path.splitext(filename)[0] + '.png'
			os.system(swfrender_cmd)
			self.__images.append(os.path.splitext(filename)[0] + '.png')

	def generate_pdf(self):
		pdf_name = self.__slide_name + ".pdf"
		print "Generating PDF..."
		aux = canvas.Canvas(pdf_name, pagesize = A4)
		lWidth, lHeight = A4
		aux.setPageSize((lHeight, lWidth)) #landscape
		#aux.setPageSize((lWidth, lHeight)) # portrait

		for filename in self.__images:
			image = os.getcwd() + '/' + filename
			#canvas.drawImage(self, image, x,y, width=None,height=None,mask=None)
			aux.drawImage(image, 60, 10) # 400,0,130,150
			aux.showPage()
		aux.save()
 		print "Done."
 	
 	def generate_ppt(self):
 		pdf_name = self.__slide_name + ".ppt"
 		print "Generatin PPT..."
 		ppLayoutBlank = 12 # Slide Type's
		Application = win32com.client.Dispatch("PowerPoint.Application")
		Application.Visible = True
		Presentation = Application.Presentations.Add();

		for filename in reversed(self.__images):
			pictName = os.getcwd() + '/' + filename
			im = Image.open(pictName)
			width, height = im.size
			Slide1 = Presentation.Slides.Add(1, ppLayoutBlank);
			Pict1 = Slide1.Shapes.AddPicture(FileName=pictName, LinkToFile=False, SaveWithDocument=True, Left=0, Top=0, Width=width, Height=height)
 		print "Done."

		Presentation.SaveAs(os.getcwd() + '/' + self.__slide_name + ".pptx");
		Application.Quit()


 	def get(self, url):
		self.url = url
		self.set_xml_file()
		self.create_directory(self.__slide_name)
		self.download()
		self.convert_to_images()
		self.generate_pdf()
		self.generate_ppt()

def main():
	slide = SlideShare()
	#slide.get("http://www.slideshare.net/oisin/simple-web-services-with-sinatra-and-heroku-6882369")
	#slide.get("http://www.slideshare.net/barrasozky/miembros")
	#slide.get("http://www.slideshare.net/RobleJose/vectorgrunge")
	#slide.get("http://www.slideshare.net/david.motta/modelo-del-negocio-con-rup-y-uml-parte-1")
	#slide.get("http://www.slideshare.net/david.motta/modelo-del-negocio-con-rup-y-uml-parte-3")
	slide.get("http://www.slideshare.net/david.motta/modelo-del-negocio-con-rup-y-uml-parte-3-1534304")
	# suggest it
	#arc = raw_input("Ingrese url: ")
	#print arc
	#slide.get(""+arc)
if __name__ == "__main__":
	main()