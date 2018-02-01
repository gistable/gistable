"""
One of our editors thought it would be fun to run a year-end list of our
most-shared stories. This script uses the Facebook API to fetch stats for 
a given list of URLs.


The script will:

- create a csv file that's named based on the value of TOP_URLS_FILE. This 
file logs URLs that have enough shares to surpass your TOP_THRESHHOLD number.

This file is updated throughout the loop, on each match.

- create a txt file that's named based on the value of COUNTING_STATS_FILE. 
It logs raw numbers for URLs that surpass the TOP_THRESHHOLD, MEDIUM_THRESHOLD 
and SMALL_THRESHOLD values. It also logs the total number of URLs scanned.

This file is updated only when the loop finishes, so an exception or a lost
connection will drop these stats. I added this tracking just out of curiosity,
but didn't really feel like adding the overhead of writing to file every
single time through the loop.

- create a file called `failed_urls.txt` to log URLs that ... fail. Once in
a while Facebook throws a bad status code, which particularly sucks when
you're on day 27 of a 30-day run. Logging failed URLs in this file allows 
your loop to keep on going. Later on, just run the failed URLs manually.


Notes:

- the sleep interval is set at 2.5 seconds because Facebook seems to cut you 
off after ~600 requests at a 1-second interval. At this interval, I've been 
able to run off a month at a time without trouble. (For us, that's about 3,000
story URLs.)

"""
import sys, traceback, optparse, urllib2, time
from lxml import etree
from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta


# ------------------
# SET US UP THE VARS
# ------------------

TOP_URLS_FILE = "top_urls.csv"
COUNTING_STATS_FILE = "counting_stats.txt"

TOP_THRESHHOLD = 100
MEDIUM_THRESHOLD = 10
SMALL_THRESHOLD = 1

SLEEP_SECONDS = 2.5


# --------------
# CUSTOMIZE THIS
# --------------

def build_url_list_to_parse(start, end):
    '''
    Rewrite this function to fetch your list of URLs in what way
    seems best to you.
    
    main() down below will pass in two datetime objects like so:
    
        url_list = build_url_list_to_parse(start, end)
    
    '''
    from django.conf import settings
    from cannonball.stories.models import Story

    story_list = Story.live_objects.filter(pubdate__gte=start, pubdate__lt=end).order_by('pubdate')
    url_list = []
    for story in story_list:
        url_list.append('http://www.spokesman.com'+story.get_absolute_url())
    
    return url_list


# ---------
# UTILITIES
# ---------

def add_url_to_top_urls(like_count, total_count, share_count, url):
    f = open(TOP_URLS_FILE, "a")
    record = "%s,%s,%s,%s\n" % (like_count, total_count, share_count, url)
    f.write(record)
    f.close()


def update_counting_stats(start, end, url_counting_dict):
    f = open(COUNTING_STATS_FILE, "a")
    record = "Period: %s through %s\n%s\n\n" % (start, end, url_counting_dict)
    f.write(record)
    f.close()


def update_stats_for_url(like_count, total_count, share_count, url, url_counting_dict):
    if total_count >= TOP_THRESHHOLD:
        add_url_to_top_urls(like_count, total_count, share_count, url)
        url_counting_dict['top_urls'] += 1
    if total_count >= MEDIUM_THRESHOLD:
        url_counting_dict['medium_urls'] += 1
    if total_count >= SMALL_THRESHOLD:
        url_counting_dict['small_urls'] += 1


def fetch_facebook_stats_for_url(url, url_counting_dict):
    # Make the proper FB url and fetch it
    api_url = 'https://api.facebook.com/method/fql.query?query=select%%20%%20like_count,%%20total_count,%%20share_count,%%20click_count%%20from%%20link_stat%%20where%%20url=%%22%s%%22' % url
    
    try:
        facebook_xml = urllib2.urlopen(api_url)

        # Get the XML object
        tree = etree.parse(facebook_xml)
    
        # Namespace madness in lxml. Punting. Throw string at BeautifulSoup
        tree = etree.tostring(tree)
        soup = BeautifulSoup(tree)
    
        #Get the stats we want
        like_count = int(soup.like_count.contents[0])
        total_count = int(soup.total_count.contents[0])
        share_count = int(soup.share_count.contents[0])
    
        # Pass off to the stats functions
        update_stats_for_url(like_count, total_count, share_count, url, url_counting_dict)
    except:
        f = open("failed_urls.txt", "a")
        record = "'%s',\n" % (url)
        f.write(record)
        f.close()


# -------------
# RUN THE THING
# e.g. >> python collect_facebook_stats.py --start=2011-01-01 --end=2011-01-31
# -------------

def process_options(arglist=None):
    global options, args
    parser = optparse.OptionParser()
    parser.add_option(
        '-s', '--start', '--start_date',
        dest='start_date',
        help="Start date for Facebook stat collection.")
    parser.add_option(
        '-e', '--end', '--end_date',
        dest='end_date',
        help="End date for Facebook stat collection.")
    options, args = parser.parse_args(arglist)
    return options, args


def main(args=None):
    """
    To run, enter something like the following at a command line:
    python collect_facebook_stats.py --start=2011-01-01 --end=2011-01-31
    
    A csv file will be created and named based on your TOP_URLS_FILE value;
    this file will log any URL that surpass your TOP_THRESHHOLD share number.

    A txt file will be created and named based on your COUNTING_STATS_FILE
    value; it will log raw numbers for URLs that surpass your TOP_THRESHHOLD,
    MEDIUM_THRESHOLD, and SMALL_THRESHOLD values.

    """
    
    if args is None:
        args = sys.argv[1:]
    options, args = process_options(args)
    
    try:
        f = open(TOP_URLS_FILE)
        f.close()
    except:
        f = open(TOP_URLS_FILE, "a")
        record = "Likes,Total,Shares,URL\n"
        f.write(record)
        f.close()
    
    url_counting_dict = {
        'top_urls': 0,
        'medium_urls': 0,
        'small_urls': 0,
        'urls_scanned': 0,
    }
    
    start = datetime.strptime(options.start_date,'%Y-%m-%d')
    end = datetime.strptime(options.end_date,'%Y-%m-%d')+timedelta(days=1)
    
    url_list = build_url_list_to_parse(start, end)
    url_counting_dict['urls_scanned'] = len(url_list)
    
    for url in url_list:
        print url
        fetch_facebook_stats_for_url(url, url_counting_dict)
        time.sleep(SLEEP_SECONDS)
        
    update_counting_stats(options.start_date, options.end_date, url_counting_dict)
    
    
if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        sys.stderr.write('\n')
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write('\n')
        sys.exit(1)

