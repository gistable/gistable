"""
Reddit Scraper

Examples
----------
$ python get_reddits.py
"""
import requests
import bs4


URL = "https://www.reddit.com/r/MachineLearning/"


def preprocess_text(text):
    """Remove tags like [P], [D], [R]"""
    return text[3:].strip()


def find_listing(bs):
    """Get articles soups

    Parameters
    ----------
    bs : bs4 object

    Returns
    ----------
    listing : bs4 object
    """
    return bs.find_all("div", {"data-context": "listing"})


def get_info(list_, base_url="https://www.reddit.com"):
    """Get title/href links

    Parameters
    ----------
    list_ : list
        bs4 listing

    Returns
    ----------
    title_list : list
    link_list : list
    """
    title_list = [item.find("a", {"data-event-action": "title"}).get_text() for item in list_]
    link_list = [base_url + item.find("a", {"data-event-action": "comments"})["data-href-url"] for item in list_]

    title_list = list(map(preprocess_text, title_list))

    return title_list, link_list


def print_list(title_list, link_list):
    """Print titles/links in format"""

    print("Title")
    print("=" * 50)
    for idx, title in enumerate(title_list[2:]):
        print(f"{idx}. {title}")

    print()
    print("Link")
    print("=" * 50)
    for idx, link in enumerate(link_list[2:]):
        print(f"{idx}. {link}")


def main():
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, sdch, br",
        "accept-language": "en-US,en;q=0.8,ko;q=0.6,zh-CN;q=0.4,zh;q=0.2",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"
    }
    reddit = requests.get(URL, headers=headers)

    bs = bs4.BeautifulSoup(reddit.text, 'html.parser')

    reddit_post_list = find_listing(bs)

    title_list, link_list = get_info(reddit_post_list)

    print_list(title_list, link_list)


if __name__ == '__main__':
    main()
