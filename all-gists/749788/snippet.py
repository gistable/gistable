#!/usr/bin/env python2

__license__   = 'GPL v3'
__copyright__ = '2010, Zsolt Botykai <zsoltika@gmail.com>'
'''
es.hu
'''
import string, re

from calibre.web.feeds.news import BasicNewsRecipe
from calibre.ebooks.BeautifulSoup import Tag, NavigableString
from string import capwords

temp_files = []
articles_are_obfuscated = True


class EletEsIrodalom(BasicNewsRecipe):

    delay = 100
    simultaneous_downloads = 1
    timeout = 60

    title      = "E'let e's Irodalom"
    __author__ = 'Zsolt Botykai'
    description = "E'let e's Irodalom"
    INDEX = 'http://www.es.hu/'
    language = 'hu'

    remove_javascript = True
    remove_empty_feeds = True
    remove_tags = [
                       dict(name='div', attrs={'id':[ 'right', \
                                                         'banner', \
                                                         'head_left', \
                             'head_right', \
                             'menu', \
                             'foot', \
                             'leaddocument' \
                             'separator' \
                             'left' \
                       ]}) , 
                       dict(name='div', attrs={'class':[ 'skybanner', \
                             'clearfloat' \
                             'separator' \
                             'almenu' \
                       ]})
               ]

    no_stylesheets = True
    timeout = 7
    delay = 3

    preprocess_regexps = [(re.compile(r'<!--.*?-->', re.DOTALL), lambda m: '')]

    def get_obfuscated_article(self, url):
        br = self.get_browser()
        br.open(url+'&print')

        response = br.follow_link(url, nr = 0)
        html = response.read()

        self.temp_files.append(PersistentTemporaryFile('_fa.html'))
        self.temp_files[-1].write(html)
        self.temp_files[-1].close()
        return self.temp_files[-1].name


    def parse_index(self):
        articles = []

        soup = self.index_to_soup(self.INDEX)
        sectit = soup.find('div', attrs={'class':'fpdocument'})
        if sectit is not None:
            texts = self.tag_to_string(sectit).strip().split()[-2:]
            if texts:
                self.timefmt = ' [%s]'%(' '.join(texts))

        cover = soup.find('img', src=True, attrs={'class':'cover'})
        if cover is not None:
            self.cover_url = cover['src']

        feeds = []
        for section in soup.findAll('div', attrs={'class':'fpdocument'}):
            section_title = section.find('a', attrs={'class':'rovat'})
            section_title = string.capwords(self.tag_to_string(section_title))
            self.log('Found section:', section_title)
            articles = []

            litem = section.find('li')
            if litem:
                for post in section.findAll('li'):
                    h = post.find(self)
                    title = self.tag_to_string(post).replace(":"," ")
                    a = post.find('a', href=True)
                    url = a['href']
                    if url.startswith('/'):
                        url = 'http://www.es.hu'+url
                    p = post.find('p', attrs={'align':'left'})
                    desc = None
                    self.log('\tFound article:', title, 'at', url)
                    if p is not None:
                        desc = self.tag_to_string(p)
                        self.log('\t\t', desc)
                    articles.append({'title':title, 'url':url, 'description':desc,
                        'date':''})
            else:
                    arttitle = section.find('a', attrs={'class':'title'})
                    if arttitle:
                            arttitstr = self.tag_to_string(arttitle)
                            artauthor = section.find('div', attrs={'class':'author'})
                            arttitl = arttitstr

                            if artauthor:
                                    artautstr = self.tag_to_string(artauthor)
                                    if artautstr != '':
                                            arttitl = capwords(artautstr)
                                            arttitl = arttitl + ' - '
                                            arttitl = arttitl + arttitstr
                            else:
                                    arttitl = arttitstr

                            title = arttitl.replace(":"," ")

                            a = section.find('a', href=True, attrs={'class':'title'})
                            url = a['href']
                            if url.startswith('/'):
                                url = 'http://www.es.hu'+url
                            self.log('\tFound article:', title , 'at', url)
                            articles.append({'title':title, 'url':url, 'description':'',
                                'date':''})



            feeds.append((section_title, articles))

        return feeds

    def preprocess_html(self, soup):
        for links in soup.findAll('a'):
            url = links['href']
            if url == '/':
                links.extract() 
        for prmattrs in ['float: right;margin-left: 5px; margin-bottom: 5px;', 'doc_tags']:
            for item in soup.findAll('div', attrs={'style':prmattrs}): 
                item.extract()

        mytitle = soup.find('div', attrs={'class':'doc_title'})
        if mytitle:
            mytitstr = self.tag_to_string(mytitle)
        myauthor = soup.find('div', attrs={'class':'doc_author'})
        if myauthor:
            myautstr = self.tag_to_string(myauthor)
            myauthor.extract()
            myntitle=myautstr + " - "
            myntitle=myntitle + mytitstr
        else:
            myntitle=mytitle
                
        tag = Tag(soup, "h2")
        tag['class'] = "headline"
        tag.insert(0, capwords(myntitle))
        mytitle.replaceWith(tag)

        mysubtitle = soup.find('div', attrs={'class':'doc_subtitle'})
        if mysubtitle:
            mysubtitstr = self.tag_to_string(mysubtitle)
            tag = Tag(soup, "h3")
            tag['class'] = "headline"
            tag.insert(0, capwords(mysubtitstr))
            mysubtitle.replaceWith(tag)
    
        mylapszam =  soup.find('div', attrs={'class':'lapszam'})
        if mylapszam:
            mylapstr = self.tag_to_string(mylapszam)
            tag = Tag(soup, "h5")
            tag['class'] = "headline"
            tag.insert(0, mylapstr)
            mylapszam.replaceWith(tag)
                
        return soup



    def get_cover_url(self):
        return 'http://www.es.hu/images/logo.jpg'

    def postprocess_html(self, soup, first):
        for rmattrs in [  'almenu', 'doc_author_docs', 'doc_print' ]:
            for item in soup.findAll('div', attrs={'class':rmattrs}): 
                item.extract()
        for pz in soup.findAll('p', attrs={'align':'left'}): 
            myp = self.tag_to_string(pz)
            if re.search('^( |&#160;)*$',myp):
                tag = Tag(soup, "div")
                tag['class'] = "removable"
                tag.insert(0, '')
                pz.replaceWith(tag)
            for brz in soup.findAll('br'):
                tag = Tag(soup, "div")
                tag['class'] = "removable"
                tag.insert(0, '')
                brz.replaceWith(tag)

        return soup

    
