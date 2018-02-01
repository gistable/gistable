import sys
from StringIO import StringIO
from bs4 import BeautifulSoup
import urlparse
import pycurl
import urllib
from mrjob.job import MRJob


USER_AGENT='Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.0
.3705; .NET CLR 1.1.4322)'

def build_url(fullname, website):
    fullname = urllib.quote_plus(fullname)
    website = urllib.quote_plus(website)
    return "https://www.google.com/search?hl=en&safe=on&site=imghp&tbm=isch&sour
ce=hp&biw=1920&bih=1019&q=site%3A" + website + "+" + fullname + "&oq=site%3A" + 
website + "+" + fullname


def get_image_for_person(fullname, website):
    pageContents = StringIO()

    c = pycurl.Curl()
    c.setopt(c.WRITEFUNCTION, pageContents.write)
    url = build_url(fullname, website)
    url=str(url.encode('utf-8'))
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.USERAGENT, USER_AGENT)
    c.perform()
    c.close()
    pageContents.seek(0)

    data = pageContents.getvalue()
    soup = BeautifulSoup(data)

    img_res = soup.find(id="ires")
    first_img = img_res.find_all("a")[0]
    href = first_img.get("href")
    params = urlparse.parse_qs(urlparse.urlparse(href).query)
    print(params["imgurl"][0])
    return params["imgurl"][0]


def stripper(x):
    return x.strip()

class MRWordCounter(MRJob):
    def mapper(self, key, line):
        tokens = map(stripper, line.split("|"))
        person_id = tokens[0]
        if person_id != "id":
            fullname = tokens[1]
            if tokens[2] != "NULL" and tokens[2] != "":
                fullname = fullname + " " + tokens[2]   
            
            fullname = fullname + " " + tokens[3]     
            website  = tokens[5]
            info = fullname + "|" + website     
            if website != "NULL":
                yield person_id, info  # key, info 

    def reducer(self, person_id, infos):
        for info in infos:
            try:
                tokens = info.split("|")
                name = tokens[0]
                website = tokens[1]
                image_url = get_image_for_person(name, website)         
                yield person_id, image_url  
                return
            except:
                pass    

if __name__ == '__main__':
    MRWordCounter.run()
