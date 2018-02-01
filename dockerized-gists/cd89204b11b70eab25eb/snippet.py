from bs4 import BeautifulSoup
import requests
import shutil
import glob
from os import listdir
from os.path import isfile, join


def save_image(url, filename):
  response = requests.get(url, stream=True)
  if response.status_code == 200:
    with open(filename, 'wb') as out_file:
      shutil.copyfileobj(response.raw, out_file)   
    del response
    return True
  else:
    del response
    return False

def scrape_xkcd_comics(c_range, folder):
  existing = [ f for f in listdir(folder) if isfile(join(folder,f))]
  existing = map(lambda x: x.split(".")[0], existing)
  
  to_download = filter(lambda x: str(x) not in existing, c_range)
  already_done = filter(lambda x: str(x) in existing, c_range)
  print "The following are already done, so skipping it:", already_done
  
  for c in to_download: 
    xkcd = requests.get("http://xkcd.com/{}".format(c))
    soup = BeautifulSoup(xkcd.text)
    comic = soup.find("div", {"id": "comic"})
    if comic is not None :
       if comic.img is None:
         print "{} does not have an image tag".format(c)
         continue
       url = comic.img["src"]
       if url.endswith("png"):
           file_name = "comics/{}.png".format(c)
       elif url.endswith("jpg"):
           file_name = "comics/{}.jpg".format(c)
       elif url.endswith("gif"):
           file_name = "comics/{}.gif".format(c)
       else:
           print "Skipping {}".format(c)
           continue
       ret = save_image("http:{}".format(url), file_name)
       if ret:
           print c, "done"
       else:
           print "Couldn't do {} for some reason. Damn!".format(c)
    else:
       print "Couldn't scrape {}".format(c)


scrape_xkcd_comics(range(1511), "comics")
