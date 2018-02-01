#! /usr/bin/env python3
"""cheat_downloader.py
Loads Chrome's cookies into Python Requests for bulk downloading.
http://n8henrie.com/2013/11/use-chromes-cookies-for-easier-downloading-with-python-requests/

Working with:
- Python 3.3.2
- BeautifulSoup 4.3.1
- Requests 2.0.0
- Chrome 30.0.1599.101
- OS X 10.9
- sqlite3.version 2.6.0
- sqlite3.sqlite_version 3.8.1
"""

import requests
import bs4
import sqlite3
import os 
import logging

def main():
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='2013-10-29 16:59:04',
        # filename='/path/log.log',
        # filemode='a'
        )
    
    logger_name = str(__file__) + " :: " + str(__name__)
    logger = logging.getLogger(logger_name)
    
    # Part of the domain name that will help the sqlite3 query pick it from the Chrome cookies
    domain = 'example.com'
    cookie_file = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Cookies')

    conn = sqlite3.connect(cookie_file)
    sql = '''select name, value from cookies where host_key like "%{}%"'''.format(domain)

    cookies = {}
    cookies_list = []

    for row in conn.execute(sql):
         cookies_list.append(row)
    cookies.update(cookies_list)

    # The base directory that you're trying to download files from.
    # Note that I left the page number left so I could iterate through them.
    base_url = 'http://example.com/get/this/directory?page='
    
    # The root directory for the files, which used relative links.
    download_base = 'http://example.com'

    s = requests.Session()

    articles = []    

    # Modify the range to suit the number of pages needed to iterate through.
    for page in range(1, 5):
        url = base_url + str(page)    
        content = s.get(url, cookies=cookies).content
        url = base_url + str(page)
        soup = bs4.BeautifulSoup(content)
        
        # Customize below to suit what links you'll want to be grabbing.
        # http://www.crummy.com/software/BeautifulSoup/bs4/doc/
        # This one grabbed links titled "PDF" and used the link before that's title
        # so I could name the files. Will differ case by case. Compiles titles and links
        # into a list of tuples.
        for link in soup.find_all('a', text='PDF'):
            if link.has_attr('href'):
                title = link.findPrevious('a').text            
                download_link = download_base + link['href']
                articles.append((title, download_link))

    # Downloads the tuples of title, link.
    for title, download_link in articles:
        outfile = '/path/to/folder/' + title + '.pdf'
        if os.path.isfile(outfile):
            logger.warning('Filename {} already exists. Perhaps you should rename?'.format(title))
            pass
        else:
            logger.info('{} doesn\'t exist, downloading.'.format(title))
            file_content = s.get(download_link).content
            with open(outfile, 'wb') as writer:
                writer.write(file_content)
                
if __name__ == '__main__':
    main()