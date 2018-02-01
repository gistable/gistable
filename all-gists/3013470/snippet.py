# hn_screen_scraper.py
# A screen scraper for the front page of hacker news done out of a fit of boredom.
from urllib  import request
import re

# read in the data and split it into a raw list of entries
url_path = "http://news.ycombinator.com"
sock = request.urlopen(url_path)
raw_data = str(sock.read())
data_set = re.split("arrow\.gif", raw_data)
data_set = data_set[1:] #first entry always the url to ycombinator.  Omitting.

url_list = []
rough_list = []

# cut out a chunk of the urls.
for line in data_set:
    start = line.find("<a")
    end = line.find("</a", start)
    the_url = line[start:end]
    rough_list.append(the_url)

# compreshensions can do the rest of the cleanup for the urls.
url_list = [x[x.find("\"")+1:] for x in rough_list]
url_list = [x[0:x.find("\"")] for x in url_list]

# grab the titles
titles = [x[x.rfind(">")+1:] for x in rough_list]

def get_comment_count(data_rec):
    pattern = r"[0-9]{,3}\ comment[s]{0,1}"
    m = re.search(pattern, data_rec)
    if  m:
        comment_count = data_rec[m.start():m.end()]
        comment_count = comment_count.split()[0]
        comment_count = int(comment_count)
        return comment_count
    return 0

# piece toegether the dictionary.
hn_articles = []
for i, url in enumerate(url_list):
    cc = get_comment_count(data_set[i])
    d = {'url':url, 'title':titles[i], 'comments':cc}
    hn_articles.append(d)

# dump it to con and order it by most commented
check_comments = lambda x:x['comments']
hn_articles = sorted(hn_articles, key=check_comments, reverse=True)
for hn_article in hn_articles:
    print( "TITLE: %s" % hn_article['title'] )
    print("URL: %s" % hn_article['url'])
    print("%d comments\n" % hn_article['comments'])
