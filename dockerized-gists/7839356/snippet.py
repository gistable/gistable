import sys
import requests

from arango import create

from bs4 import BeautifulSoup


HEADERS = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5)",
    "accept": "text/html,application/xhtml+xml,application/xml;"
              "q=0.9,*/*;q=0.8",
    "accept-charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
    "accept-encoding": "gzip,deflate,sdch",
    "accept-language": "en-US,en;q=0.8",
}


def username(nodes):
    """
    Extract twitter username
    """
    return nodes.find(
        class_="js-user-profile-link").attrs["href"][1:]


def tweet(nodes):
    return nodes.find(class_="tweet-text").text


def permalink(nodes):
    return nodes.find(class_="js-permalink").attrs["href"]


def download(link):
    url = "https://twitter.com/{url}".format(url=link)
    r = requests.get(url, headers=HEADERS)

    # check the status code of the response to make sure the request went well
    if r.status_code != 200:
        print("request denied")
        return None

    return BeautifulSoup(r.text)


def context(result):
    return {
        "name": result.find(class_="fullname").contents[0],
        "user": username(result),
        "text": tweet(result),
        "link": permalink(result)}


def details(link):
    result = download(link).find_all(class_="tweet-stats-container")[0]
    for item in result.find_all(class_="js-profile-popup-actionable"):
        yield item.attrs["href"][1:]


def scrape(arango, src, depth=0, max_depth=5, from_doc=None):
    if depth > max_depth:
        return

    results = download(src).find_all(class_="stream-item")

    for ctx in [context(result) for result in results]:
        if ctx["user"] != src:
            continue

        to_doc = arango.tweets.documents.create(ctx)
        if from_doc is not None:
            arango.tweets_edges.edges.create(from_doc, to_doc)

        favorited_users = list(details(ctx["link"]))
        if favorited_users:
            print("{}>{}: {}".format(
                "--" * depth, ctx["name"], ctx["text"]))
            for fv in favorited_users:
                scrape(
                    arango, fv, depth=depth + 1,
                    max_depth=max_depth, from_doc=to_doc)


if __name__ == "__main__":
    print("Usage: ./scrape.py keyword max_depth")
    # you can pass in a keyword to search for when you run the script
    # be default, we'll search for the "web scraping" keyword
    try:
        keyword = sys.argv[1]
    except IndexError:
        keyword = "maxmaxmaxmax"

    try:
        depth = int(sys.argv[2])
    except (IndexError, TypeError, ValueError):
        depth = 5

    arango = create(db="tweets_{}".format(keyword))
    arango.database.create()
    arango.tweets.create()
    arango.tweets_edges.create(
        type=arango.COLLECTION_EDGES)

    scrape(arango, keyword, max_depth=depth)
