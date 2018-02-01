from bs4 import BeautifulSoup
from itertools import count
import requests

url = 'http://alpha.wallhaven.cc/search?categories=101&sorting=favorites&order=desc&page='
jpg = 'http://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-%s.jpg'
png = 'http://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-%s.png'

status = '\r[page {:0>3}] [image {:0>2}|24] [{:.<24}]'.format

for i in count(1):
    soup = BeautifulSoup(requests.get(url + str(i)).text)
    figs = soup.find_all('figure')
    for j, fig in enumerate(figs, 1):
        print status(i, j, j*'#'),
        name = fig.find('a').get('href').rsplit('/', 1)[1]
        r = requests.get(jpg % name)
        if r.status_code == 404:
            r = requests.get(png % name)
            name += '.png'
        else:
            name += '.jpg'
        with open('%03d-%02d-%s' % (i, j, name), 'wb') as f:
            f.write(r.content)
