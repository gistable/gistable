import os
import re
import sys
import requests

filename_matcher = re.compile(r'http://www.oreilly.com/(.*)/free/(.*).csp')

def main():
    categories = sys.argv[1:]
    urls = map(lambda x: 'http://www.oreilly.com/{}/free/'.format(x), categories)
    for (category, url), filenames in zip(zip(categories, urls), map(retrieve_filenames, urls)):
        print(category)
        if not os.path.exists(category):
            os.makedirs(category)
        for title, (book_category, files) in filenames.items():
            path = os.path.join(category, title)
            if not os.path.exists(path):
                os.makedirs(path)
            print '\t{}'.format(title)
            for file in files:
                print('\t\t{}'.format(file))
                download_file(os.path.join(category, title, file),
                              'http://www.oreilly.com/{}/free/files/{}'.format(book_category, file))


def download_file(path, url):
    response = requests.get(url, stream=True)
    with open(path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def retrieve_filenames(url):
    response = requests.get(url).text
    matches = filename_matcher.findall(response)
    return {
        name: (category, map(lambda x: x.format(name), ['{}.pdf', '{}.mobi', '{}.epub']))
        for (category, name) in matches
    }


if __name__ == '__main__':
    main()
