import urllib2
from BeautifulSoup import BeautifulSoup
from mechanize import Browser
import re
 
def getunicode(soup):
    body=''
    if isinstance(soup, unicode):
        soup = soup.replace("'","'")
        soup = soup.replace('&quot;','"')
        soup = soup.replace('&nbsp;',' ')
        body = body + soup
    else:
        if not soup.contents:
          return ''
        con_list = soup.contents
        for con in con_list:
          body = body + getunicode(con)
    return body
 
def main():
  movie = str(raw_input('Tell me the Movie Name: '))
  movie_search = '+'.join(movie.split())
 
  base_url = 'http://www.imdb.com/find?q='
  url = base_url+movie_search+'&s=all'
 
  title_search = re.compile('/title/tt\d+')
 
  br = Browser()
 
  br.open(url)
 
  link = br.find_link(url_regex = re.compile(r'/title/tt.*'))
  res = br.follow_link(link)
 
  soup = BeautifulSoup(res.read())
 
  movie_title = getunicode(soup.find('title'))
  rate = soup.find('span',itemprop='ratingValue')
  rating = getunicode(rate)
  actors=[]
  actors_soup = soup.find(**{'class':"cast_list"}).findAll('span',itemprop='name')
  for i in range(len(actors_soup)):
    actors.append(getunicode(actors_soup[i]))
 
  des = soup.find('meta',{'name':'description'})['content']
 
  genre=[]
  infobar = soup.find('div',{'class':'infobar'})
  r = infobar.find('',{'title':True})['title']
  genrelist = infobar.findAll('a',{'href':True})
 
  for i in range(len(genrelist)-1):
    genre.append(getunicode(genrelist[i]))
  release_date = getunicode(genrelist[-1])
  print "+"*80 
  print movie_title,rating+'/10.0'
  print 'Relase Date:',release_date
  print 'Rated',r
  print ''
  print 'Genre:',
  print ', '.join(genre)
  print '\nActors:',
  print ', '.join(actors)
  print '\nDescription:'
  print des
  print "-"*80
 
if __name__ == '__main__':
    main()