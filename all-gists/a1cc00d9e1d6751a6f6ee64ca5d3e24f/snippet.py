#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests

POKEURL = 'http://cmmcd.com/PokemonGo/'

r = requests.get(POKEURL)
try:
    import lxml
    soup = BeautifulSoup(r.text, 'lxml')
except ImportError:
    soup = BeautifulSoup(r.text, 'html.parser')

status = soup.body.header.h2.font.text

if __name__ == '__main__':
    if status == 'Unstable!':
        print('  PKGO Shaky!')
    elif status == 'Offline!':
        print('  PKGO Down!')
    else:
        exit(0)
