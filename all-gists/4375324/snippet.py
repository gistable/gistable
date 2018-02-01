"""
 -------------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <calzoneman@gmail.com> wrote this file. As long as you retain this notice you
 * can do whatever you want with this stuff. If we meet some day, and you think
 * this stuff is worth it, you can buy me a drink in return
 * - Calvin Montgomery
 -------------------------------------------------------------------------------
"""

"""
Usage:
python tunes.py [subreddit name] ([more subreddits] ...)

For all links and no embedded content:
python tunes.py --no-embed [subreddit name] ([more subreddits] ...)
(--no-embed can be abbreviated -ne)
"""

import urllib2
import json
import sys
import time
import HTMLParser
import re

# Extract only URLs coming from these domains
WHITELIST = ["youtube.com", "soundcloud.com"]
# Whether or not to include embedded sources (e.g. youtube iframes)
ALLOW_EMBED = True
# Whether to generate static HTML or a YTQ playlist
GENERATE_YTQ = False

def read_reddit(subreddit):
    req = urllib2.Request("http://api.reddit.com/r/" + subreddit, None, {})
    opener = urllib2.build_opener()
    opener.addheaders = [("User-Agent", "Tunes bot by /u/calzoneman")]
    f = opener.open(req)
    return json.load(f)["data"]["children"]

def filter_posts(posts, domains):
    return [post for post in posts if post["data"]["domain"] in domains]

def sort_posts(posts):
    return sorted(posts, key=lambda post: post["data"]["score"], reverse=True)

def parse_yturl(url):
    url = url[url.find("youtube"):]
    m = re.match("youtube\\.com/watch\\?v=([^&]*)", url)
    if(m):
        return m.group(1)
    else:
        return None

def to_html(posts):
    """
    Thanks to kalgynirae <http://github.com/kalgynirae>
    for making this function a lot cleaner
    """
    h = HTMLParser.HTMLParser()
    page_start = """
<!doctype html>
<html>
    <head>
        <title>TUNES</title>
        <style type="text/css">
            table, td, th {
                border: 1px solid #000000;
                font-family: Monospace;
            }
        </style>
    </head>
    <body>
        <table>
            <tr>
                <th>Score</th>
                <th>Subreddit</th>
                <th>Content</th>
            </tr>"""
    post_template = """
            <tr>
                <td>{score}</td>
                <td>{subreddit}</td>
                <td>{content}</td>
            </tr>"""
    page_end = """
        </table>
    </body>
</html>"""
    def content(post):
        if ALLOW_EMBED and "content" in post["data"]["media_embed"]:
            return h.unescape(post["data"]["media_embed"]["content"])
        else:
            return '<a href="{}">{}</a>'.format(post["data"]["url"],
                                                post["data"]["title"])
    post_htmls = (post_template.format(
                      score=post["data"]["score"],
                      subreddit=post["data"]["subreddit"],
                      content=content(post))
                  for post in posts)
    page = page_start + ''.join(post_htmls) + page_end
    return page.encode('ascii', 'xmlcharrefreplace')

subs = sys.argv[1:]
if sys.argv[1] == "--no-embed" or sys.argv[1] == "-ne":
    ALLOW_EMBED = False
    subs = sys.argv[2:]
if sys.argv[1] == "--ytq" or sys.argv[1] == "-y":
    GENERATE_YTQ = True
    WHITELIST = ["youtube.com"]
    subs = sys.argv[2:]
posts = []
for i, sub in enumerate(subs):
    print "Reading /r/" + sub
    posts.extend(read_reddit(sub))
    if i < len(subs) - 1:
        time.sleep(5)

posts = filter_posts(posts, WHITELIST)
posts = sort_posts(posts)

if GENERATE_YTQ:
    plist = []
    for post in posts:
        parsed = parse_yturl(post["data"]["url"])
        if parsed:
            plist.append(parsed)

    url = "http://aperture.calzoneman.net/calzoneman/ytq/index.html"
    url += "?playlist=" + ",".join(plist)
    print url
else:
    fname = "-".join(subs) + time.strftime("-%Y-%M-%d_%H%M") + ".html"
    with open(fname, "w") as f:
        f.write(to_html(posts))

    print "Dumped to " + fname