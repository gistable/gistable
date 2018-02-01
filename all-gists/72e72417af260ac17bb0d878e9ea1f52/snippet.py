import re
from urllib.parse import quote

import requests
from tqdm import tqdm

def main():
    with open('crossref.json', 'w') as _out:
        bar = tqdm()
        cursor = '*'
        while True:
            response = requests.get('http://api.crossref.org/works?rows=1000&cursor=' + cursor)
            match = re.search(r'\"next-cursor\"\:\"(.*?)\"', response.text)
            _out.write(response.text + '\n')

            if not match:
                break

            cursor = quote(match.group(1).replace('\\/', '/'))
            bar.update()


if __name__ == '__main__':
    main()
