#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#   xkcd.py
#
# xkcd comic grabber


from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup

def get_page(n):
    page = urlopen('http://xkcd.com/%d/' % n)
    return page.read()

def make_soup(content):
    return BeautifulSoup(content)

def get_title(soup):
    text = soup.html.title.text
    return text.split(':')[1].strip()

def get_image(soup, title):
    line = soup.find('img', alt=title)
    return line['src']

def copy_image(url, n):
    img = urlopen(url)
    content = img.read()
    name = 'comic-%d.jpg' % n
    out = open(name, 'w')
    out.write(content)
    out.close()

def main():
    number = 20
    page = get_page(number)
    soup = make_soup(page)
    image = get_image(soup, get_title(soup))
    copy_image(image, number)

if __name__ == '__main__':
    main()