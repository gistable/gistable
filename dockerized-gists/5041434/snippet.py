import requests
from bs4 import BeautifulSoup, NavigableString


def get_review_text(block):
    """Get just the text of a review from it's DIV"""
    strings = []
    for possible_text in block.children:
        if isinstance(possible_text, NavigableString):
            stripped_text = possible_text.strip()
            if len(stripped_text) > 0:
                strings.append(stripped_text)
    return "\n".join(strings)


def get_review_texts(review_html):
    """Get all the reviews on a review page"""
    soup = BeautifulSoup(review_html)
    table = soup.find(id="productReviews").tr.td
    review_blocks = table.find_all("div", recursive=False)
    return [get_review_text(block) for block in review_blocks]


def get_review_page_count(review_html):
    """Get the number of review pages"""
    soup = BeautifulSoup(review_html)
    try:
        return int(soup.find("span", class_="paging").find_all("a")[-2].text)
    except:
        return 1


def get_all_reviews(review_url):
    """Get all the reviews, given a review page URL"""
    # sanitize the url
    review_url = "/".join(review_url.split("/")[:-1])

    first_review_page = requests.get(review_url).text
    review_page_count = get_review_page_count(first_review_page)
    reviews = []
    for i in range(1, review_page_count + 1):
        url = review_url + "?pageNumber=%d" % i
        review_html = requests.get(url).text
        reviews.extend(get_review_texts(review_html))
    return reviews