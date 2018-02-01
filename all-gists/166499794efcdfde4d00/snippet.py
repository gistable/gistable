import re, os
import urllib
import ImageFile
import photos
import clipboard
from bs4 import BeautifulSoup
from PIL import Image

def download_from(url):
	print("get content from " + url)
	opener = urllib.FancyURLopener({})
	f = opener.open(url)
	return f.read()

def mk_tempdir(path):
	try:
		os.mkdir(path)
	except OSError:
		print('tmpimage directory already exists')
	
def save_image_to_file(html_doc):
	soup = BeautifulSoup(html_doc)
	artworks = soup.find_all('img', 'artwork')
	title_head = soup.title.string.split(' ')[0]
	title_re = re.compile(title_head)
	mk_tempdir('./tmpimage')

	for a in artworks:
		if title_re.match(a['alt']):
			save_path = './tmpimage/' + title_head + '.png'
			urllib.urlretrieve(a['src-swap'], save_path)
			print('saving a image file to ' + save_path)
			return save_path

def save_image_to_ios_photo(path):
	im = Image.open(path)
	photos.save_image(im)	

def save_image_to_photos():
	store_clip = clipboard.get()
	url = store_clip.split("\n")[1]
	print url
	html_content = download_from(url)
	path = save_image_to_file(html_content)
	save_image_to_ios_photo(path)

save_image_to_photos()
