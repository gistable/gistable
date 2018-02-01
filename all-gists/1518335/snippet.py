#!/usr/bin/env python
import BeautifulSoup
import cookielib
import re
import urllib2


def parse_rating(rating):
    """Parse a rating's class name and return it as a number.

    The rating's class name is expected to follow the format set
    on the Windows Phone Marketplace. The rating should be between
    1 and 5 with half-star increments. A rating of 0 means unrated.

    >>> [parse_rating(x + 'Pt' + y)
    ...  for x in ['zero', 'one', 'two', 'three', 'four', 'five']
    ...  for y in ['zero', 'five']]
    [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5]
    """
    # Build a lookup table of values.
    values = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}

    # Split the rating around the decimal point.
    integer, fraction = rating.split('Pt')

    # Convert each part to an integer.
    integer = values[integer]
    fraction = values[fraction.lower()]

    # Combine and return the parts.
    return integer + (fraction / 10.0)


def scrape(url, jar=None):
    """Extract application data from the Windows Phone Marketplace.

    The URL is just an app's URL in the marketplace. The jar is an
    optional argument that makes scraping multiple apps faster by
    skipping the required cookie handshake on subsequent scrapes.

    Returns a tuple with the app's details as a dictionary and the
    cookie jar.

    >>> scrape(...)
    ({...}, <cookielib.CookieJar[...]>)
    """
    # Create a cookie jar if necessary.
    if jar is None:
        jar = cookielib.CookieJar()

    # Build an opener using the cookie jar.
    handler = urllib2.HTTPCookieProcessor(jar)
    opener = urllib2.build_opener(handler)

    # Fill the cookie jar if it's empty.
    if not jar:
        opener.open(url)

    # Open and parse the marketplace page.
    response = opener.open(url)
    soup = BeautifulSoup.BeautifulSoup(response)

    # Extract app information.
    info = {
        'category': {
            'name': soup.find(id='category').find('strong').string,
            'url': ('http://www.windowsphone.com' +
                soup.find(id='category').find('a')['href']),
        },
        'description': soup.find(id='appDetails').find('pre').string,
        'id': soup.find(property='og:url')['content'][-36:],
        'image': soup.find(id='appSummary').find('img')['src'],
        'name': soup.find(id='application').find('h1').string,
        'permissions': [tag.string
            for tag in soup.find(id='disclosures').findAll('li')],
        'price': soup.find('a', {'class': 'purchase'}),
        'publisher': {
            'name': soup.find(id='publisher').find('a').string,
            'url': soup.find(id='publisher').find('a')['href'],
        },
        'rating': parse_rating(soup.find('div',
            {'class': re.compile('ratingLarge .*')})['class'].split()[1]),
        'required': soup.find(id='required').string,
        'screenshots': [tag['src']
            for tag in soup.find(id='screenshots').findAll('img')],
        'url': soup.find(property='og:url')['content'],
        'version': soup.find(id='version').find('li').string,
    }

    # Parse price as a float.
    if info['price']['id'] == 'free':
        info['price'] = 0.00
    else:
        info['price'] = float(info['price'].string[-4:])

    # Remove unnecessary query string from publisher URL.
    info['publisher']['url'] = re.sub('[?].*$', '',
        info['publisher']['url'])

    # Remove resize bit from image query strings.
    info['image'] = re.sub('&resize=true', '', info['image'])
    for index, screenshot in enumerate(info['screenshots']):
        info['screenshots'][index] = re.sub('&resize=true', '', screenshot)

    return info
