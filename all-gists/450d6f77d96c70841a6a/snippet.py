#---------------------------------------------------------------#
# This script manually goes through youtube and collects all    #
# of your viewing history into a convenient text file. This     #
# might take about 30min to an hour, depending on your          #
# computer's RAM, processing speed, and internet connection.    #
# Note that this program requires the splinter module to work.  #
# Run 'pip install splinter' to get it.                         #
#---------------------------------------------------------------#
print "Making sure you're not using python 3..."
from splinter import Browser
from time import sleep
from getpass import getpass
from datetime import datetime as dt
email = raw_input(
    """Please enter your youtube google account
    email address (e.g. bobby@gmail.com): """
    )
pwd = getpass("Please enter your correpsonding password: ")
def get_href(webdriverelement):
  html = webdriverelement.outer_html
  i = html.find('href="') + 6
  j = html.find('"', i)
  return html[i:j]
def get_YT_id(webdriverelement):
  href = get_href(webdriverelement)
  i = href.find('&')
  if i == -1:
    return href
  return href[:i]
answered = False
while not answered:
  ans = raw_input("Do you want your watched videos history? (y/n) ").lower()
  if ans in ["y", "yes"]:
    watch_hist = True
    answered = True
  elif ans in ["n", "no"]:
    watch_hist = False
    answered = True
  else:
    print "Please give a valid answer"
answered = False
while not answered:
  ans = raw_input("Do you want your liked videos history? (y/n) ").lower()
  if ans in ["y", "yes"]:
    like_hist = True
    answered = True
  elif ans in ["n", "no"]:
    like_hist = False
    answered = True
  else:
    print "Please give a valid answer"
answered = False
while not answered:
  ans = raw_input("Do you want your search history? (y/n) ").lower()
  if ans in ["y", "yes"]:
    search_hist = True
    answered = True
  elif ans in ["n", "no"]:
    search_hist = False
    answered = True
  else:
    print "Please give a valid answer"
with Browser() as browser:
  browser.visit("https://youtube.com")
  buttons = browser.find_by_text('Sign in').first.click()
  browser.fill("Email", email)
  browser.find_by_id("next").click()
  browser.fill("Passwd", pwd)
  browser.find_by_id("signIn").click()
  if len(browser.find_by_id("totpPin"))>0:
    raw_input("Please finish 2-step authentication in firefox browser and press enter ")
  if watch_hist:
    print "Getting watch history"
    browser.visit("https://youtube.com/feed/history")
    i = 0
    string = ""
    old_html = ""
    while True:
      temp = browser.find_by_css(".load-more-button")
      if len(temp)>0:
        temp.first.click()
        sleep(1)
      else:
        break
      loaded = False
      while not loaded:
        titles = browser.find_by_css(".yt-uix-tile-link")
        new_i = len(titles)
        if new_i != i:
          loaded = True
      string = "\n".join([string] + [ (title.text + "\nlink:\t" + get_YT_id(title)) for title in titles[i:]])
      with open("YT_watch_hist.txt", "w") as log:
        log.write(string.encode('utf8'))
      print "Total videos loaded: %i" % new_i
      i = new_i
    print "Loaded all viewing history!!!"
  if like_hist:
    print "Getting like history"
    browser.visit("https://youtube.com/")
    temp = browser.find_by_id("VLLLjxcq1Xwce56FCsJ_g53NUg-guide-item")
    browser.visit("https://youtube.com" + get_href(temp))
    i = 0
    string = ""
    old_html = ""
    while True:
      temp = browser.find_by_css(".load-more-button")
      if len(temp)>0:
        temp.first.click()
        sleep(1)
      else:
        break
      loaded = False
      while not loaded:
        titles = browser.find_by_css(".yt-uix-tile-link")
        new_i = len(titles)
        if new_i != i:
          loaded = True
      string = "\n".join([string] + [ (title.text + "\nlink:\t" + get_YT_id(title)) for title in titles[i:]])
      with open("YT_like_hist.txt", "w") as log:
        log.write(string.encode('utf8'))
      print "Total videos loaded: %i" % new_i
      i = new_i
    print "Loaded all like history!!!"
  if search_hist:
    print "Getting search history"
    browser.visit("https://www.youtube.com/feed/history/search_history")
    i = 0
    string = str("Current time: dt.now()")
    old_html = ""
    while True:
      temp = browser.find_by_css(".load-more-button")
      if len(temp)>0:
        temp.first.click()
        sleep(1)
      else:
        break
      loaded = False
      while not loaded:
        searches = browser.find_by_css(".feed-item-main")
        new_i = len(searches)
        if new_i != i:
          loaded = True
      string = "\n".join([string] + [ search.text for search in searches[i:]])
      with open("YT_search_hist.txt", "w") as log:
        log.write(string.encode('utf8'))
      print "Total searches loaded: %i" % new_i
      i = new_i
    print "Loaded all search history!!!"
  print "Done!! Thanks for using! <3"
