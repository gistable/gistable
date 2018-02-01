from requests import get
from bs4 import BeautifulSoup
import re
import os

def make_filename(fname):
    for c in ',! ().':
        fname = fname.replace(c, '_')
    while fname != fname.replace('__', '_'):
        fname = fname.replace('__', '_')
    return fname.strip('_').lower() + '.p8.png'

id_re = re.compile(ur'thumbs\/pico(?P<id>\d+)\.png')
n_pages_re = re.compile(ur'Page \d+ of (?P<num_pages>\d+)')

CART_ADDRESS = 'http://www.lexaloffle.com/bbs/cposts/1/{id}.p8.png'

def get_carts(page):
    html = get('http://www.lexaloffle.com/bbs/?page={page}&mode=carts&cat=7&sub=2'.format(page = page)).text
    soup = BeautifulSoup(html, 'html.parser')

    carts = []

    for div in soup.find_all(style = 'border-radius: 3px;float:left;width:132px; padding:8px; margin:6px; background:#fff'):
        carts.append({'id': int(id_re.match(div.center.a.img['src']).group('id')), 'title': div.center.div.a.font.text})

    return carts

num_pages = int(n_pages_re.search(get('http://www.lexaloffle.com/bbs/?page=2&mode=carts&cat=7&sub=2').text).group('num_pages'))

os.mkdir('carts')
os.chdir('carts')
for page in range(1, num_pages + 1):
    os.mkdir('page_{page}'.format(page = page))
    os.chdir('page_{page}'.format(page = page))
    carts = get_carts(page)
    for cart in carts:
        print cart, make_filename(cart['title'])
        f = open(make_filename(cart['title']), 'wb')
        f.write(get(CART_ADDRESS.format(id = cart['id'])).content)
        f.close()
    os.chdir('..')
