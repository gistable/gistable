import sys
import urllib
import re
import random
from lxml import etree
 
class Downloader():
  '''
  Class to retreive HTML code
  and binary files from a 
  specific website
  '''
 
  def __init__(self, url):
    self.url = url
 
  def download(self, image_name='', is_image=False):
    try:
      browser = urllib.urlopen(self.url)
      response = browser.getcode()
    except:
      print 'Bad connection'
      sys.exit()

    if response == 200:
      contents = browser.read()
    else:
      print 'Bad header response'
      sys.exit()
 
    if is_image:
      self.save_image(contents, image_name)

    return contents

  def save_image(self, contents, image_name):
    image_file = open(image_name, 'wb')
    image_file.write(contents)
    image_file.close()
 

class xkcdParser():
  '''
  Class for parsing xkcd.com
  '''
 
  def __init__(self):
    self.url = "http://xkcd.com/"
    self.last_comic_nr = None
    self.contents = ''
    self.title = ''
    self.caption = ''

  def set_last_comic_nr(self):
    downloader = Downloader(self.url)
    self.contents = downloader.download()
    self.last_comic_nr = re.search(r"http://xkcd.com/(\d+)", self.contents).group(1)
    self.last_comic_nr = int(self.last_comic_nr)

  def get_current_comic(self):
    self.set_last_comic_nr()
    self.get_title()
    self.get_caption()
    self.get_comic()
 
  def get_comic_by_id(self, comic_nr):
    if not self.last_comic_nr:
      self.set_last_comic_nr()

    try:
      comic_nr = int(comic_nr)
    except:
      print 'The comic number should be an integer'
      sys.exit()

    if comic_nr <= self.last_comic_nr:
      url = self.url + str(comic_nr)
      downloader = Downloader(url)
      self.contents = downloader.download()
      self.get_title()
      self.get_caption()
      self.get_comic()

  def get_random_comic(self):
    if not self.last_comic_nr:
      self.set_last_comic_nr()

    comic_nr = random.randint(1, self.last_comic_nr)
    self.get_comic_by_id(comic_nr)
   
  def get_title(self):
    if self.contents:
      tree = etree.HTML(self.contents)
      self.title = tree.xpath("string(//div[@id='ctitle'])")
 
  def get_caption(self):
    if self.contents:
      tree = etree.HTML(self.contents)
      self.caption = tree.xpath("string(//div[@id='comic']/img/@title)")

  def get_comic(self):
    if self.contents:
      tree = etree.HTML(self.contents)
      url = tree.xpath("string(//div[@id='comic']/img/@src)")
 
      downloader = Downloader(url)
      downloader.download(self.title, True)
 
 
if __name__ == '__main__':

  xkcd_parser = xkcdParser()
  # example how to get the current comic
  xkcd_parser.get_current_comic()
  print xkcd_parser.title
  print xkcd_parser.caption

  # example how to get a comic by it's id
  xkcd_parser.get_comic_by_id(859)
  print xkcd_parser.title
  print xkcd_parser.caption

  # example how to get a random comic
  xkcd_parser.get_random_comic()
  print xkcd_parser.title
  print xkcd_parser.caption