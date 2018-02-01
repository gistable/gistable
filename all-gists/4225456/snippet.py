""" 
This script was written to illustrate libraries that could be used to improve upon
the efficiency of a script posted to /r/learnprogramming:
Original script:
  https://github.com/aesptux/download-reddit-saved-images/blob/master/script.py
Reddit post
  http://www.reddit.com/r/learnprogramming/comments/14dojd 
  /pythoncode_review_script_to_download_saved_images/
"""
from urllib2 import Request, urlopen
from StringIO import StringIO
# You probably need to download these libraries
import praw           # install with pip or easy_install
from PIL import Image # install from binary: http://www.pythonware.com/products/pil/

###########################################
## ENTER YOUR USERNAME AND PASSWORD HERE ##
###########################################
_user = 'shaggorama'
_pass = 'hunter2'

_user_agent_string = "improving on /u/aesptux's script - prototype by /u/shaggorama"
_image_formats = ['bmp','dib','eps','ps','gif','im','jpg','jpe','jpeg',
                  'pcd','pcx','png','pbm','pgm','ppm','psd','tif','tiff',
                  'xbm','xpm','rgb','rast','svg']
 
def is_image_link(submission):
    """
    Takes a praw.Submission object and returns a boolean
    describing whether or not submission links to an 
    image.
    """
    if link.subreddit.display_name == 'pics' \
      or 'imgur' in submission.domain.split('.') \
      or submission.url.split('.')[-1] in _image_formats:
        return True
    else:
        return False

r = praw.Reddit(_user_agent_string)
r.login(username=_user, password=_pass)
saved = r.get_saved_links(limit=None)

issue_links=[]
for link in saved:
    if not is_image_link(link):
        continue    
    request = Request(link.url)
    response = urlopen(request)
    data = response.read()        
    try:
        im = Image.open(StringIO(data))
        im.verify()
        
        fname=link.url.split('/')[-1]
        Image.open(StringIO(data)).save(fname)
    except:
        # Encountered issue downloading image. Image is probably somewhere in the page
        # or might not be a filetype supported by PIL
        issue_links.append(link.url)