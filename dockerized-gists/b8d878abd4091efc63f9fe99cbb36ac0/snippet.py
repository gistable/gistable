import sys
import requests
from lxml import html
import time

if len(sys.argv) < 2:
    print("Usage: {} URL [page jump limit]".format(sys.argv[0]))
    exit()

link = sys.argv[1]
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 25

#input: URL, return: root tree element
def get_page_tree(page):
    return html.fromstring(page.content)

#input: root tree, return: title of article
def get_title(tree):
    return tree.xpath('//*[@id="firstHeading"]')[0].text

#input: root tree element, return: next URL in chain
def get_first_link(tree):
    parenthesized = 0
    for p in tree.xpath('//*[@id="mw-content-text"]/p'):
        for e in p:
            if e.tag == 'a' and not parenthesized:
                return 'https://en.wikipedia.org' + e.attrib['href']

            raw = str(html.tostring(e))
            for c in raw:
                if c == '(':
                    parenthesized += 1
                if c == ')':
                    parenthesized -= 1

for step in range(limit):
    page = requests.get(link)
    tree = get_page_tree(page)
    title = get_title(tree)
    print("{}\n#{}: {}".format(link,step+1, title))
    if title == 'Philosophy':
        break
    link = get_first_link(tree)
    time.sleep(0.1)