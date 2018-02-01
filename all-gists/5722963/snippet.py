#! /usr/bin/python

from lxml import html
import datetime
import requests
from collections import defaultdict


def parse(html_string, impact=None):
        """
        send in a defaultdict(int) to get impact stats
        """
        csv = ""
        tree = html.fromstring(html_string)
        for row in tree.body.xpath("//tr"):
            tds = row.xpath("td")
            if len(tds) != 8:
                continue
            [name, kudos, year_commits, all_time_commits,
             five_year_commits, language, first_commit,
             last_commit] = tds
            # get what we really want
            name = name.getchildren()[1].text.encode('ascii', 'ignore').strip()
            first_commit = formatDate(first_commit.getchildren()[0].get('title'))
            last_commit = formatDate(last_commit.getchildren()[0].get('title'))
            year_commits = int(year_commits.text.strip())
            all_time_commits = int(all_time_commits.text.strip())
            if impact != None:
                impact[first_commit] += all_time_commits
            csv += "%s,%s,%s,%s,%s\n" % (name, first_commit,
                                         year_commits,
                                         last_commit,
                                        all_time_commits)
        return csv, impact
            


def formatDate(date):
    parts = date.split(" ")
    date = " ".join(parts[1:3] + [parts[-1]])
    return datetime.datetime.strptime(date, "%b %d %Y").strftime("%D")
            

def getDataFromSite(sort="latest_commit", pages=3):
    csv = ""
    impact_stats = defaultdict(int)
    for page in range(1, pages):
        url= "https://www.ohloh.net/p/plone/contributors?page=%s&squery=&sort=%s" % (page, sort)
        html_string = requests.get(url).text
        csv_results, impact =  parse(html_string, impact = impact_stats)
        csv += csv_results
    return csv, impact_stats


def getDataFromFiles(filenames):
    csv = ""
    impact_stats = defaultdict(int)
    for filename in filenames:
        with open(filename, 'rb') as hf:
            csv_results, impact = parse(hf.read(), impact = impact_stats)
            csv += csv_results
    return csv, impact_stats


def getLatestCommits():
    csv, impact = getDataFromSite(sort="latest_commit", pages=42)

    for date, commits in impact.items():
        print "%s,%s" % (date, commits)

    print csv


def getNewestContributors():
    csv, impact = getDataFromSite(sort="newest", pages=10)

    for date, commits in impact.items():
        print "%s,%s" % (date, commits)

    print csv


if __name__ == '__main__':
    getNewestContributors()

    

