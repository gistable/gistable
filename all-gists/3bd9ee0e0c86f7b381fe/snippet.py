# coding: utf-8
import requests
from lxml.html import fromstring
from requests_toolbelt.multipart.encoder import MultipartEncoder


def extract(soup):
    for elem in soup.cssselect('.rc h3 a'):
        href = elem.get('href')
        if 'parom.hu' not in href:
            yield {'text': elem.text_content(), 'url': href}


def reverse(fp, walk_limit=5):
    walked = 0
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36'
    m = MultipartEncoder({'encoded_image': (fp.name, fp, 'image/jpeg'), 'image_url': None, 'image_content': None, 'filename': None, 'btnG': None})

    r = requests.post('http://www.google.hu/searchbyimage/upload', data=m, headers={'Content-Type': m.content_type, 'User-Agent': user_agent})
    soup = fromstring(r.text, base_url='http://www.google.hu')
    soup.make_links_absolute()
    yield from extract(soup)

    next = soup.cssselect('#pnnext')
    while walked < walk_limit and next:
        walked += 1

        url = next[0].get('href')
        r = requests.get(url, headers={'User-Agent': user_agent})
        soup = fromstring(r.text, base_url='http://www.google.hu')
        soup.make_links_absolute()

        next = soup.cssselect('#pnnext')
        yield from extract(soup)