# Fucking scripts to download from chiasenhac, whole album!

import os
from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool

NUMBER_PROCESS = 8

MUSIC_QUALITY = '320'
ALBUM_URL = "http://chiasenhac.vn/nghe-album/she-will-be-loved~maroon-5~ts3wcmvbq9v82q.html"
DIR = "Song About Jane (2002)"


def download_file(url):
    down_page = requests.get(url).text
    down_soup = BeautifulSoup(down_page, 'html.parser')
    filename = down_soup.title.text.split(
        'Download: ')[-1].split(" - ")[0] + ".mp3"
    print "downloading file: {}".format(filename)
    for link in down_soup.find_all('a'):
        href = link.get('href')
        if href and href.find('.mp3') > 0 and href.find(MUSIC_QUALITY) > 0: # 
            with open(os.path.join(DIR, filename), 'wb') as f:
                content = requests.get(href).content
                f.write(content)


def main(url):
    org_page = requests.get(url).text
    org_soup = BeautifulSoup(org_page, 'html.parser')

    list_url = set() # link might appear twice, so use set
    for link in org_soup.find_all('a'):
        href = link.get('href')
        if href and href.find('download') > 0:
            list_url.add(href)
    print list_url

    p = Pool(processes=NUMBER_PROCESS)
    p.map(download_file, list_url)
    p.close()


if __name__ == '__main__':
    if not os.path.exists(DIR):
        os.mkdir(DIR)
    main(ALBUM_URL)
