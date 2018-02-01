# -*- coding: utf-8 -*-
"""
Builds epub book out of Paul Graham's essays: http://paulgraham.com/articles.html

Author: Ola Sitarska <ola@sitarska.com>
Copyright: Licensed under the GPL-3 (http://www.gnu.org/licenses/gpl-3.0.html)

This script requires python-epub-library: http://code.google.com/p/python-epub-builder/
"""

import re, ez_epub, urllib2, genshi
from BeautifulSoup import BeautifulSoup

def addSection(link, title):
    if not 'http' in link:
        page = urllib2.urlopen('http://www.paulgraham.com/'+link).read()
        soup = BeautifulSoup(page)
        soup.prettify() 
    else:
        page = urllib2.urlopen(link).read()
        
    section = ez_epub.Section()
    try:
        section.title = title
        print section.title

        if not 'http' in link:
            font = str(soup.findAll('table', {'width':'455'})[0].findAll('font')[0])
            if not 'Get funded by' in font and not 'Watch how this essay was' in font and not 'Like to build things?' in font and not len(font)<100:
                content = font
            else:
                content = ''
                for par in soup.findAll('table', {'width':'455'})[0].findAll('p'):
                    content += str(par)

            for p in content.split("<br /><br />"):
                section.text.append(genshi.core.Markup(p))

            #exception for Subject: Airbnb
            for pre in soup.findAll('pre'):
                section.text.append(genshi.core.Markup(pre))
        else:
            for p in str(page).replace("\n","<br />").split("<br /><br />"):
                section.text.append(genshi.core.Markup(p))
    except:
        pass
    
    return section


book = ez_epub.Book()
book.title = "Paul Graham's Essays"
book.authors = ['Paul Graham']

page = urllib2.urlopen('http://www.paulgraham.com/articles.html').read()
soup = BeautifulSoup(page)
soup.prettify()

links = soup.findAll('table', {'width': '455'})[1].findAll('a')
sections = []
for link in links:
    sections.append(addSection(link['href'], link.text))
    
book.sections = sections
book.make(book.title)