from pyquery import PyQuery
import requests
from random import choice

url = 'http://www.johnsmarketplace.com/Kegs/'

query = 'td table tr'


def main():
    possibilities = []
    resp = requests.get(url)

    pq = PyQuery(resp.text)
    for num, row in enumerate(pq.find(query)):
        if num == 0:
            continue # skip header

        if len(row.getchildren()) < 5:
            continue

        name = row.getchildren()[0].text
        kind = row.getchildren()[5].text

        if not name or 'ipa' not in name.lower():
            continue

        possibilities += [name]

    print choice(possibilities)


if __name__ == '__main__':
    main()
