##################################################################################
# O'Reilly Free Books link extractor
##################################################################################
#
#  Extracts all links from O'Reilly website to automate free eBook download.
#  Looks for existing files in the current directory to avoid downloading the same
#  book twice.
#
##################################################################################
#
# Dependencies: request and BeautifulSoup
#
# $ sudo pip3 install requests bs4
#
##################################################################################
#
# Usage:
#
# $ python3 oreilly-free-books.py
# $ wget -i books.txt
#
# If you want to perform parallel downloads, you can use aria2c instead of wget
#
# $ aria2c -x 16 -s 16 -i books.txt
#
##################################################################################

import requests
from bs4 import BeautifulSoup
import os

root_url = 'http://www.oreilly.com/free/reports.html'
links = []

# Get filenames in current directory
files = [f for f in os.listdir('.') if os.path.isfile(os.path.join('.', f))]
filenames = [os.path.splitext(os.path.basename(f))[0] for f in files]

root_web = requests.get(root_url)
root_soup = BeautifulSoup(root_web.text)

book_categories_url = [a['href'] for a in root_soup.find_all('a', class_='large-btn')]

for url in book_categories_url:
    category_web = requests.get(url)
    category_soup = BeautifulSoup(category_web.text)
    books = [a['href'] for a in category_soup.find_all('a') if a.get('data-toggle', None) and '.csp' in a['href']]
    for book in books:
        title = book[book.rfind('/'):book.rfind('.')]
        if title not in filenames:
            index = book.find('/free/')+6
            links += [book[:index]+'files/'+book[index:].replace('.csp', i) for i in ['.pdf', '.mobi', '.epub']]

with open('books.txt', 'w') as f:
    f.writelines([l+'\n' for l in links])