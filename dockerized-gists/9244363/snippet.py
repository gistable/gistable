from gdata import service
import gdata
import atom
import feedparser
from time import *

banner = """
    Blogger Automatic Content Generation and Publication
    Coded by Ricky L. Wilson
    Post entries from RSS feeds to a blogger blog using Googles Blogger API.
    Don't go to crazy Blogger only alows 50 post's a day 
"""
print banner

blog_id  = ''
email    = ''
password = ''
source   = 'My blog'
feeds = ["http://stackoverflow.com/feeds/"]
limit = 2

# Programmatically log in to blogger
blogger_service = service.GDataService(email,password)
blogger_service.source = source
blogger_service.service = 'blogger'
blogger_service.account_type = 'GOOGLE'
blogger_service.server = 'www.blogger.com'
blogger_service.ProgrammaticLogin()

def CreatePublicPost(blogger_service, blog_id, title, content):
  entry = gdata.GDataEntry()
  entry.title = atom.Title('xhtml', title)
  entry.content = atom.Content(content_type='html', text=content)
  return blogger_service.Post(entry, '/feeds/%s/posts/default' % blog_id)

def publishFeed(url,limit=0):
  d = feedparser.parse(url)
  feed_title        = d.feed.title
  feed_description  = d.feed.description
  feed_entries      = d.entries
  n_entries = len(feed_entries)
  n_posted  = 0
  for i in feed_entries:
    if n_posted <= limit:
      title = i.title
      link = i.link
      description = i.description
      if title and link and description and title not in titles_posted:
        try:
          print "Posting %s" % (title)
          print "%d posts posted" % (n_posted)
          post = CreatePublicPost(blogger_service, blog_id,title,description)
          n_posted = n_posted + 1
        except gdata.service.RequestError:
          print "Blog has exceeded rate limit of 50 or otherwise\nrequires word verification for new posts"
          print "Should be back in action tomorow"
          quit()
      else: pass

def main(feeds,limit,delay):   
  while True:
    for feed in feeds:
      publishFeed(feed,limit)
      sleep(delay)

main(feeds,limit,delay)
