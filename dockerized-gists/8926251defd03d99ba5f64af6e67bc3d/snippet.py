# I am not the author of this script. I just keep it here because it is infinitely useful.
__author__ = 'Jan'
import base64

from bs4 import BeautifulSoup
import cfscrape
from pySmartDL import SmartDL
import os.path
import argparse


def get_episodes(url, kissanime=False):
    html = scraper.get(url).content
    soup = BeautifulSoup(html, "lxml")

    table = soup.find("table", "listing")

    tablesoup = BeautifulSoup(str(table), "lxml")

    links = []

    for link in tablesoup.findAll('a'):
        if kissanime:
            links.append("%s%s" % ("http://kissanime.com", link.get('href')))
        else:
            links.append("%s%s" % ("http://kisscartoon.me", link.get('href')))
    return links


def get_episode(url, quiet=False, quality=False):
    html = scraper.get(url).content
    soup = BeautifulSoup(html, "lxml")
    link = soup.find("select", {"id": "selectQuality"})
    valuesoup = BeautifulSoup(str(link), "lxml")
    dlinks = []
    quali = []
    for src in valuesoup.findAll('option'):
        quali.append(src.text)
        dlinks.append(base64.b64decode(src.get('value')))
    if not quiet:
        if quality:
            print("Quality : " + quali[len(quali)-1])
        else:
            print("Quality : " + quali[0])
    return dlinks


def download(url, name, quiet = False):
    path = ".%s%s" % (os.sep, name)
    if os.path.isfile(path):
        if not quiet:
            print "Skipping %s" % name
        return
    else:
        obj = SmartDL(url, path)
        try:
            obj.start()
        except KeyboardInterrupt:
            obj.stop()



parser = argparse.ArgumentParser()
parser.add_argument("show")
parser.add_argument("-l","--only-links", help="only print's the links. doesn't download the files.", action="store_true")
parser.add_argument("-s","--save-links", help="saves the links to links.txt", action="store_true")
parser.add_argument("-a","--low-quality", help="reduces the quality", action="store_true")
parser.add_argument("-q","--quiet", help="shut's up", action="store_true")
args = parser.parse_args()


scraper = cfscrape.create_scraper()

show = args.show

showname = show.split("/")[-1]
if not args.quiet:
    print("Serie : %s" % showname)

links = []

for episode in list(reversed(get_episodes(show, "kissanime" in show))):
    episodename = episode.split("/")[-1].split("?")[0] + ".mp4"
    if not args.quiet:
        print "Episode : %s" % episodename
    qualitys = get_episode(episode, args.quiet, args.low_quality)
    if args.low_quality:
        link = qualitys[len(qualitys)-1]
    else:
        link = qualitys[0]

    if args.only_links:
        print(link)
    else:
        download(link, "%s_%s" % (showname, episodename), args.quiet)

    if args.save_links:
        links.append(link)
    print("\n")
if args.save_links:
    with open('links.txt', 'a') as file:
        for link in links:
            file.write("%s" % (link) )


