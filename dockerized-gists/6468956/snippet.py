from selenium import webdriver
from random import choice
import time

b = webdriver.Firefox()
b.get("http://www.nytimes.com/interactive/2013/09/02/sports/tennis/tennis-grunts-soundboard.html")
grunt_div = b.find_element_by_id('nytmm')
face_divs = grunt_div.find_elements_by_tag_name('div')

interval = [float(s)/100 for s in range(50,151,1)]

while True:
  face = choice(face_divs)
  try:
    face.click()
    # time.sleep(choice(interval))
  except:
    continue
