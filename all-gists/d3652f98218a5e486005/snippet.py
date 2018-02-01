#!/usr/bin/python3
import requests, subprocess, time, smtplib

from email.mime.text import MIMEText
from bs4 import BeautifulSoup

class BitcoinPrice:
    price = 0
    website = "http://www.bitcoinexchangerate.org/"

    def _getSite(self):
        rawHtml = requests.get(self.website).text
        return rawHtml

    def _parseSite(self, rawHtml):
        site = BeautifulSoup(rawHtml)
        titleString = site.title.string
        priceString = ""
        #iterate through webpage title and grab the numbers
        for char in titleString:
            if char.isdigit() or char == ".":
                priceString += char #add digit to string
            elif(char == 'U'): #end on the USD
                break
        return priceString

    def _getPriceFromWeb(self):
        self.price = float(self._parseSite(self._getSite()))

    def getPrice(self):
        return self.price

    def updatePrice(self):
        self._getPriceFromWeb()

    def __init__(self):
        self._getPriceFromWeb()


priceObj = BitcoinPrice()
USERNAME = input("Input Gmail Address: ")
PASSWORD = input("Input Gmail Password: ")
PHONEADDRESS = input("Input Phone Email: ")
buyPrice = float(input("Input what price you want to buy at: "))

def craftEmail(price, toAddress):
    msg = MIMEText("Hey you need to go buy some bitcoin at trucoin the price is only $" + price + ".")
    msg["Subject"] = "Buy Bitcoin"
    msg["From"] = "Bitcoin Bot"
    msg["To"] = toAddress
    return msg

def sendEmail(msg, recipient, USERNAME, PASSWORD):
    session = smtplib.SMTP("smtp.gmail.com", "587")
    session.ehlo()
    session.starttls()
    session.login(USERNAME, PASSWORD)
    session.sendmail(USERNAME, recipient, msg.as_string())

while True: #Main loop that will send the text and Push Alert
    price = priceObj.getPrice()
    if price <= buyPrice:
        subprocess.call(['notify-send', 'Buy Bitcoins!', 'Price: $' + str(price)])
        sendEmail(craftEmail(str(price), PHONEADDRESS), PHONEADDRESS, USERNAME, PASSWORD)
        time.sleep(300)
        priceObj.updatePrice()
        continue
    priceObj.updatePrice()
    time.sleep(300)