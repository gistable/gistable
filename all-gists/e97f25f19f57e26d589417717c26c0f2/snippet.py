from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import datetime
import csv

start = datetime.datetime.now()


def get_countries(url):
    try:
        # Visit and read page
        req = Request(url, headers={'User-Agent': 'BlocCrawl'})
        open_country = urlopen(req).read()
        soup = BeautifulSoup(open_country, "html.parser")
        table = soup.find_all("table", attrs={"class": "table table-striped "})
    except Exception as e:
        return "{0}:{1} on {2}".format(type(e).__name__, str(e), url)

    new_soup = BeautifulSoup(str(table[0]), "html.parser")
    super_clean_table = []

    # Finds all nation links
    for link in new_soup.findAll('a'):
        if "#" not in link.get('href') and "rankings.php?page" not in link.get('href') and "alliancestats.php" not in link.get('href'):
            super_clean_table.append(link.get('href'))

    # Returns all nation links in a page
    return super_clean_table


def get_nation(url):
    try:
        # Visit and read page
        req = Request(url, headers={'User-Agent': 'BlocCrawl'})
        open_country = urlopen(req).read()
        # Put page into BeautifulSoup class for Parsing
        soup = BeautifulSoup(open_country, "html.parser")
        # Find all tables with the class 'table table-striped...'
        table = soup.find_all("table", attrs={"class":
                                              """table table-striped
                                              table-condensed table-hover
                                              table-bordered"""})
    except Exception as e:
        # Catches and returns exception
        return "{0}:{1} on {2}".format(type(e).__name__, str(e), url)

    for i in range(0, len(table)):
        table[i] = table[i].get_text()

    war_check = ""
    war_country = ""
    alliance = ""

    # Puts the html for tables into one string
    for i in range(0, len(table)):
        for t in table[i]:
            clean_table = BeautifulSoup(str(t), "html.parser")
            war_check += clean_table.prettify()

    # Checks if the nation is at war
    new_soup = BeautifulSoup(war_check, "html.parser")
    for link in new_soup.findAll('a'):
        if '/stats.php' in link.get('href'):
            table.append(link.get('href'))

    table.append(alliance)
    table.append(war_country)

    n = [i.split('\n\n') for i in table]
    n = [x for y in n for x in y]
    n = list(filter(None, n))
    n = [i.replace('\n', "") for i in n]
    return n

crawled = 0

if __name__ == '__main__':
    # Crawls all ranking pages for nation urls, then crawls nation urls for nation info
    for i in range(1, 12):  # Number will increase, needs a way to track
        print("Page {}".format(i))
        for c in get_countries('http://www.blocgame.com/rankings.php?page=' + str(i)):
            with open('test.csv', 'a') as db:
                wr = csv.writer(db, quoting=csv.QUOTE_ALL)
                wr.writerow(get_nation('http://www.blocgame.com/' + str(c)))
            crawled += 1

# Uses 15k mem
taken = datetime.datetime.now() - start
with open('bloccrawl.txt', 'a') as f:
    print("Took {} to complete".format(str(taken)), file=f)
    print("\nCrawled: " + str(crawled), file=f)
    print("\nAverage of {} to crawl".format(str(taken/crawled)), file=f)
