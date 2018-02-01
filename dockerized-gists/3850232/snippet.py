#!/usr/bin/python
# -*- coding: utf-8 -*-

# Parsea la página de busquedas de DailyMotion para encontrar
# episodios de Detective Conan, busca las URL y las imprime,
# para usar junto con JDownloader

import urllib2
import time
from BeautifulSoup import BeautifulSoup

def url_episodio(num):

  url = 'http://www.dailymotion.com/relevance/search/detective+conan+' + str(num) + '/1'

  page = urllib2.urlopen(url)
  soup = BeautifulSoup(page)

  # el primer elemento h3 de la página
  h3 = soup.findAll('h3')[0]
  link = h3.a
  return 'http://www.dailymotion.com' + link['href']

if __name__ == '__main__':
  for i in range(581, 600):
    print url_episodio(i)
