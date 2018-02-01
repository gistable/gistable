import requests
from bs4 import BeautifulSoup
import sys

def get_content(url):
    
    r = requests.get(url)
    r.raise_for_status()
    return r.text


def create_md_link(title, url):
    return '[{}]({})'.format(title, url)


if __name__ == '__main__':
    
    url = sys.argv[1]
    soup = BeautifulSoup(get_content(url), 'lxml')
    title = soup.head.title.string
    md_link = create_md_link(title, url)
    print(md_link, end='')