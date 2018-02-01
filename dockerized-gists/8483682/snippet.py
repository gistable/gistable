"""
Scrape a user's Netflix movie ratings by automating a Safari browsing
session (with the user already logged in).  The ratings are written
as tab-delimited UTF-8 encoded text in a plain text file.

This Python script is for terminal-savvy Mac users.


To use
======

0.  The script requires the Python lxml XML parsing library, and the Jinja2
template library; neither is in the Python standard library.  If you have
the pip Python package manager installed, installation is simple ("$"
represents the terminal prompt and should not be typed):

  $ pip install lxml
  $ pip install jinja2

For more installation instructions, see the project web pages:

  lxml:  http://lxml.de/
  Jinja2:  http://jinja.pocoo.org/docs/

1.  The script is set up for scraping ratings from a user's DVD account.
If instead you want to scrape ratings from a streaming account, adjust the
initial URL setting in the script (search for "initial URL" below;
instructions are there).

2.  Launch Safari, navigate to Netflix, and log in to your account.

3.  In an open Terminal or iTerm window, in the directory where this
script resides, run the script using Python:

  $ python ScrapeNetflixRatings.py

4.  Be patient; the script must go page by page through all of your
ratings.  It waits 4 seconds before scraping each page to make sure
Safari finishes loading and rendering the content.  After that, the
actual scraping and parsing is very fast.  Collecting ~500 ratings
takes about 2 minutes.  Progress is reported to the terminal session
page by page.

5.  The script writes the collected ratings to "NetflixRatings.txt" as
tab-delimited UTF-8 encoded plain text.  The choice of tab delimiters
and the ".txt" suffix are for compatibility with Apple Numbers:  if
you open the file with Numbers, it will automatically be converted
to a spreadsheet.  (This won't work if the file is a ".csv" CSV file
with comma delimiters; movie titles with commas in their names foul
up the import, even when the titles are single- or double-quoted.)


Approach
========

This script scrapes the user's ratings web pages, instead of using
Netflix's database API, because at the time of writing the Netflix API
does not support collecting all of a user's ratings (although some hacks
can get ratings of previously rented movies).  Although such capability
was once planned, after years of hemming and hawing it appears Netflix
has decided not provide this capability; see:

  Netflix API Feature Requests:  Get all of a user's ratings
  http://developer.netflix.com/forum/read/28216


Notes for maintenance/updating
==============================

There are several Greasemonkey and Ruby scripts available online for
accomplishing this task.  At the time of writing, none of them worked,
presumably due to Netflix's changes in the format of the ratings pages.  The
discussion logs for some of these tools indicate that this is a recurring
problem.  It is thus likely that this script will need modification sooner
rather than later.

This script parses Netflix's HTML source using the Python lxml library, and
locates content in the resulting DOM tree of page elements using XPath
syntax.  For a brief intro to lxml parsing of HTML (in the context of using 
the Python requests library for web scraping, rather than AppleScript as used
here) see:

  http://docs.python-guide.org/en/latest/scenarios/scrape/

The script handles authentication in a somewhat crude manner:  it uses
AppleScript to control a Safari session, with the user already logged in
to Netflix.  The AppleScript script is run in a subprocess, and returns
the HTML to this script via stdout capture.  (Python-based scraping
tools that might provide more elegant alternatives include mechanize,
scrapy, and requests.)

After parsing to a DOM tree, the needed data is located using XPath syntax. 
This is the part most likely to need maintenance as Netflix changes the HTML
used on the ratings pages.  If the script fails, navigate to a sample page
in Safari and view the HTML using the Developer menu.  Identify the HTML
elements containing the relevant text data, and update the XPath strings in
the script to match them. Note that Netflix sometimes uses elements with
multiple class names. Selecting these with XPath is tricky; see the comments
in the script for more about this.


Created Jan 17, 2014 by Tom Loredo
"""

import subprocess, codecs

from jinja2 import Template
from lxml import html


# AppleScript functions asrun and asquote (presently unused) are from:
# http://www.leancrew.com/all-this/2013/03/combining-python-and-applescript/

def asrun(ascript):
  """
  Run the given AppleScript and return its standard output.
  """
  osa = subprocess.Popen(['osascript', '-'],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
  return osa.communicate(ascript)[0]  # return stdout

def asquote(astr):
  """
  Return the AppleScript equivalent of the given string.
  """
  astr = astr.replace('"', '" & quote & "')
  return '"{}"'.format(astr)


# To deal with Netflix authentication, we assume the user has an open
# Safari browser, and has already logged in to Netflix.  We use Safari's
# scriptability via AppleScript to get HTML from pages in the user's
# account.  This approach is borrowed from Hugh Watkins's Ruby script:
#
#   https://gist.github.com/hwatkins/1425290


# AppleScript template to get HTML source from the frontmost Safari page:
ASTemplate = Template("""\
tell application "Safari"
  activate
  set url of document 1 to "{{URL}}"
  delay {{DTIME}}
  set htmlSource to source of document 1
  set s to htmlSource as text
end tell
""")


def get_parse(url, dtime):
    """
    Get the source of the page with URL=`url` (after waiting `dtime` seconds
    for rendering), parse it, and return a list of movie info, and the
    URL of the next page of ratings (or None if there are no further ratings
    pages).
    
    The movie info is a list of tuples:  (title, year, genre, rating).
    All values are strings.
    """
    # Load the page, grab the HTML, and parse it to a tree.
    script = ASTemplate.render(URL=url, DTIME=dtime)
    reply = asrun(script)
    tree = html.fromstring(reply)
    rows = tree.xpath('//table[@class="listHeader"]//tr')
    
    # Row data elements:
    #  Queue button | Title/year/alt-title | Genre | Rating
    info = []
    for i, row in enumerate(rows):
        data = row.xpath('.//td')
        # title = row.xpath('.//td[@class="list-title"]')
        tdata = data[1].xpath('.//div[@class="list-title"]')
        if tdata:
            title = tdata[0].xpath('.//span[@class="title"]')[0].text_content().strip()
            year = tdata[0].xpath('.//span[@class="list-titleyear"]')[0].text_content().strip()
            genre = data[2].xpath('.//div[@class="list-genre"]')[0].text_content().strip()
            # rating = data[3].xpath('//div[@class="list-rating"]')
            # Note that the rating class has multiple values, some of them
            # changing from page to page.  For info on XPath for such cases, see:
            # http://stackoverflow.com/questions/8808921/selecting-a-css-class-with-xpath
            # rating = data[3].xpath('//span[@class="stbrMaskFg sbmfrt sbmf-50"]')[0].text_content()
            rating = data[3].xpath('//span[contains(concat(" ", normalize-space(@class), " "), " stbrMaskFg ")]')[0].text_content()
            rating = rating.split(':')[1].strip()  # keep only the number
            info.append((title, year, genre, rating))
    
    # Next URL to load:
    next_elem = tree.xpath('//li[@class="navItem paginationLink paginationLink-next"]/a')
    if next_elem:
        next_url = next_elem[0].get('href')
    else:  # empty list
        next_url = None
    
    return info, next_url


# Use this initial URL for DVD accounts:
url = 'http://dvd.netflix.com/MoviesYouveSeen'
# Use this initial URL for streaming accounts:
# url = 'http://movies.netflix.com/MoviesYouveSeen'

dtime = 4  # seconds to wait for page to render

info = []
n = 0
while True:
    print 'Scraping', url
    page_info, url = get_parse(url, dtime)
    for entry in page_info:
        n += 1
        print '%i:  %s %s [%s] - %s' % (n, entry[0], entry[1], entry[2], entry[3])
    print
    info.extend(page_info)
    if url is None:
        break

# Save to a tab-delimited .txt file to enable importing with Numbers.
# (Numbers gets confused by titles with commas in them in CSV files,
# even when enclosed in double or single quotes.)
with codecs.open('NetflixRatings.txt', 'w', 'utf-8-sig') as ofile:
    for i, entry in enumerate(info):
        ofile.write('%i\t%s\t%s\t%s\t%s\n' % (i+1, entry[0], entry[1][1:-1], entry[2], entry[3]) )
