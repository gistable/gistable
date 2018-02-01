#!/usr/bin/env python2
# Script to check for new GOG Connect games
#
# Configure your system for sending emails first. I used:
# https://www.howtoforge.com/tutorial/configure-postfix-to-use-gmail-as-a-mail-relay/
import requests
import browsercookie
import json
import smtplib
from email.mime.text import MIMEText

# Fill in your email here
EMAIL = ""

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0"

# Load cookies from Firefox
session.cookies = browsercookie.firefox()
# Uncomment for Chrome
#session.cookies = browsercookie.chrome()

user_data = json.loads(session.get("https://www.gog.com/userData.json").text)

# Refresh Steam products
refresh_url = "https://www.gog.com/api/v1/users/{}/gogLink/steam/synchronizeUserProfile".format(
    user_data["userId"]
)

session.get(refresh_url)

steam_products_url = "http://www.gog.com/api/v1/users/{}/gogLink/steam/exchangeableProducts".format(
    user_data["userId"]
)

steam_products = json.loads(session.get(steam_products_url).text)

games_available = False
for key, value in steam_products["items"].items():
    if value["status"] == "available":
        games_available = True
        break

if games_available:
    print("New games available!")
    msg = MIMEText("Redeem them here:\nhttps://gog.com/connect/")
    msg["Subject"] = "New GOG Connect games available!"
    msg["From"] = EMAIL
    msg["To"] = EMAIL
    s = smtplib.SMTP("localhost")
    s.sendmail(EMAIL, [EMAIL], msg.as_string())
    s.quit()
else:
    print("No new games available")
