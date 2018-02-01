#!/usr/bin/python
import gtk
import simplejson
import urllib2
import subprocess
import datetime
import string
import random
import time

# !!! DEPENDS ON NOTIFY OSD BINARIES FOR NOTIFICATIONS !!!
# sudo apt-get install libnotify-bin

############################################
#    CONFIGURATION                         #
############################################

DROPBOX_USER_ID = None # REPLACE WITH YOUR DROPBOX PUBLIC ID
DROPBOX_PUBLIC_PATH = "/home/username/Dropbox/Public/"  # CHANGE USERNAME - ensure paths end in /
WAIT_FOR_DROPBOX = True  # don't exit script and return URL until upload is complete
SUB_PATH = ""  # used if you don't want screengrabs in root public dir, make sure this path exists

# URL SHORTENER API SETTINGS
USE_URL_SHORTENER = True
API_PATH = "http://is.gd/create.php?format=json&url=$longurl"  # $longurl will be replaced with image URL
API_RESPONSE_TYPE = "json"  # or "plain"
JSON_SHORTURL_KEY = "shorturl"  # if using "json" above provide the keyname of the short response

############################################
#    END CONFIGURATION                     #
############################################


subprocess.call(["gnome-screenshot", "-c", "-a"])

clipboard = gtk.Clipboard()
content = clipboard.wait_for_image()

filename = "%s_%s.png" % (
	datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S"),
	''.join(random.choice(string.ascii_uppercase) for x in range(5))
)

content.save(
	"%s%s%s" % (
		DROPBOX_PUBLIC_PATH,
		SUB_PATH,
		filename),
	"png"
)

if USE_URL_SHORTENER:
	api_url = string.Template(API_PATH).substitute(
		longurl="http://dl.dropbox.com/u/%d/%s/%s" % (
			DROPBOX_USER_ID,
			SUB_PATH,
			filename
		)
	)

	response = urllib2.urlopen(api_url)

	if API_RESPONSE_TYPE == "json":
		res_dict = simplejson.loads(response.read())
		shorturl = res_dict[JSON_SHORTURL_KEY]

	elif API_RESPONSE_TYPE == "plain":
		shorturl = response.read()
else:
	shorturl = "http://dl.dropbox.com/u/%d/%s/%s" % (
		DROPBOX_USER_ID,
		SUB_PATH,
		filename
	)

clipboard.set_text(shorturl)
clipboard.store()

if WAIT_FOR_DROPBOX:
	subprocess.call(["notify-send", "Screengrab is being uploaded...", "--hint=int:transient:1"])
	while subprocess.check_output(['dropbox', 'status'])[:4] != "Idle":
		time.sleep(2)

subprocess.call(["notify-send", "Screengrab posted. URL copied to clipboard", shorturl, "--hint=int:transient:1"])
