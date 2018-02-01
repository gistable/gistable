import os, sys, re, io, json, time
import mechanize
import pytz
import smtplib
import bs4

from datetime import datetime, timedelta
from pytz import timezone
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from datetime import date

# Configuration
url = "http://www.reserveamerica.com/camping/nehalem-bay-state-park/r/campgroundDetails.do?contractCode=OR&parkId=402191" # url of your desired campground
lengthOfStay = "2" # how many days you plan to stay
siteCode = "A01,A02" # the codes of your favorite camp sites here
date = "08/21/2015" # the date you want to check

# Create browser
br = mechanize.Browser()

# Browser options
br.set_handle_equiv(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1);
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]; 
br.open(url); 

# Fill out form
br.select_form(nr=0)
br.form.set_all_readonly(False) # allow changing the .value of all controls
br.form["campingDate"] = date
br.form["lengthOfStay"] = lengthOfStay
br.form["siteCode"] = siteCode
response = br.submit()

# Scrape result
soup = BeautifulSoup(response, "html.parser")
table = soup.findAll("table", {"id": "shoppingitems"})
rows = table[0].findAll("tr", {"class": "br"})
hits = []

for row in rows :
    cells = row.findAll("td")
    l = len(cells)
    label = cells[0].findAll("div",{"class": "siteListLabel"})[0].text
    status = cells[l-1].text
    if( status.startswith( 'available' ) ):
        hits.append(label)

if( len(hits) > 0 ):
    hdisplay = ', '.join(hits)
    hsend = '\n'.join(hits)
    print "%s : found available sites --> %s" % (date, hdisplay )