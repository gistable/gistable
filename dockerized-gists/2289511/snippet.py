import re
import time
import pprint
import urllib2
import urllib

from BeautifulSoup import BeautifulSoup as soup
from random import choice

def append_links(thumb_div):
    for thumb in thumb_div:
        print '---', thumb
        for a_href in thumb.findAll('a'):
            link = a_href.get('href')
            if re.search('^http://wallbase.cc/wallpaper/*', link):
                links.append(link)

def get_src(link):
    print 'getting: %s' % link
    this_soup = soup(urllib2.urlopen(urllib2.Request(link)).read())
    return this_soup.findAll('div', attrs={'id':'bigwall'})[0].findAll('img')[0].get('src')

def get_loop(links, save_directory):

    for i in range(10):
        img_src = get_src(choice(links))
        file_name = img_src.split('/').pop()
        print file_name
        print 'getting: %s' % img_src
        print urllib.urlretrieve(img_src, save_directory + file_name)
        
        nap = choice(range(120))
        print 'sleeping for %s seconds' % nap
        time.sleep(nap)

if __name__ == '__main__':

    user_name = 'username'
    save_directory = '/Users/%s/Pictures/wallbase_toplist/' % user_name

    while(1):

        links = []

        nap = choice(range(120))
        page = choice(range(10)) * 60

        url = 'http://wallbase.cc/toplist/%s/213/eqeq/0x0/0/100/60/3d' % page

        print 'grabbing: %s' % url

        this_soup = soup(urllib2.urlopen(urllib2.Request(url)).read())
        divs = this_soup.findAll('div', attrs={'class':re.compile('thumb*')})
        pprint.pprint(divs)

        append_links(divs)

        # divs = that_soup.findAll('div', attrs={'class':re.compile('thumb*')})
        # print 'Got links to %s wallpapers.' % len(links)

        pprint.pprint(links)

        get_loop(links, save_directory)

        print 'sleeping for %s seconds' % nap
        time.sleep(nap)
