#!/usr/local/bin/python
from BeautifulSoup import BeautifulSoup as bs
import urllib2
import datetime
import sys

username = sys.argv[1]

def Export(username, pages):
    for page in range(int(pages)):
        page = int(page) + 1
        url = 'http://www.mobypicture.com/user/' + username + '/' + str(page) + '/list'
        try:
            soup = bs(urllib2.urlopen(url).read())
            titles = soup.findAll("a", "item_info_title_photo", limit=10)
            dates = soup.findAll("div","posted_on", limit=10)
            images = soup.findAll('img',"imageLinkBorder", limit=10)

            c_titles = []
            for title in titles:
                c_titles.append(title.contents[0].replace('&nbsp;','').replace(':','-'))

            c_dates = []
            for date in dates:
                f = date.contents[0].replace('Posted ','')
                try:
                    f = f.split(' ')
                    c_dates.append(f[2] + '_' + f[1] + '_' + f[0] + '_' + f[3].replace(':','-'))
                except:
                    c_dates.append('_'.join(f))
                
            c_images = []
            for image in images:
                c_images.append(image['src'].replace('small','full'))

            for i in range(9):    
                opener = urllib2.build_opener()
                image = opener.open(str(c_images[i]))
                image = image.read()
    
                filename = str(c_dates[i]) + '_' + str(c_titles[i]) + '.jpg'
                print filename  #test
                fout = open(filename, "wb")
                fout.write(image)
                fout.close()
        except:
            print "Something went wrong parsing the page.."

try:            
    user = 'http://www.mobypicture.com/user/' + username + '/list'
    page = bs(urllib2.urlopen(user).read())
    pages = page.findAll('a','page_number').pop(-2).contents[0]       
except:            
    print 'Something went wrong, does the user exist?'     

print "Go an grab a cup of coffee, the script currently exporting all pages. All scraped images will be shown below: "
       
Export(username,pages)
    

    
