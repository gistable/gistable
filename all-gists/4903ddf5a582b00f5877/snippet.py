#!/usr/bin/env python
# encoding: utf-8
"""
pbic_pricing_scraper.py
Created by Robert Dempsey on 09-29-2015
Copyright (c) 2015 Robert Dempsey. All rights reserved.

Utility script to obtain the price information for my book: Python Business Intelligence Cookbook
http://pythonbicookbook.com/
"""

# Import requests, BeautifulSoup4(bs4), csv and datetime

import requests
import bs4
import csv
from datetime import datetime


# Cleaners
def remove_all_whitespace(x):
    """
    Returns a string with any blank spaces removed.
    """
    try:
        x = x.replace(" ", "")
    except:
        pass
    return x


def trim_the_ends(x):
    """
    Returns a string with space on the left and right removed.
    """
    try:
        x = x.strip(' \t\n\r')
    except:
        pass
    return x


def remove_unneeded_chars(x):
    """
    Returns the string without the unneeded chars
    """
    try:
        x = x.replace("$", "").replace("RRP", "")
    except:
        pass
    return x

# Grab the web page on the Packt website
URL = ("https://www.packtpub.com/application-development/"
       "python-business-intelligence-cookbook")
       
# Use response to get the page
response = requests.get(URL)

# Save the response to the soup so we can parse it
soup = bs4.BeautifulSoup(response.text)

# Extract the pricing data using the class of the elements
price_ebook = soup.select('.book-top-pricing-main-ebook-price ')[1].get_text()
price_book = soup.select('.book-top-pricing-main-book-price ')[0].get_text()
price_rrp_ebook = soup.select('.book-top-pricing-rrp-ebook')[0].get_text()
price_rrp_book = soup.select('.book-top-pricing-rrp-book')[0].get_text()

# Clean the pricing data
price_ebook = remove_all_whitespace(price_ebook)
price_ebook = trim_the_ends(price_ebook)
price_ebook = remove_unneeded_chars(price_ebook)

price_book = remove_all_whitespace(price_book)
price_book = trim_the_ends(price_book)
price_book = remove_unneeded_chars(price_book)

price_rrp_ebook = remove_all_whitespace(price_rrp_ebook)
price_rrp_ebook = trim_the_ends(price_rrp_ebook)
price_rrp_ebook = remove_unneeded_chars(price_rrp_ebook)

price_rrp_book = remove_all_whitespace(price_rrp_book)
price_rrp_book = trim_the_ends(price_rrp_book)
price_rrp_book = remove_unneeded_chars(price_rrp_book)

# Append the pricing data to the CSV file
pricing_file = ("/Users/robertdempsey/Dropbox/private/Python Business "
                "Intelligence Cookbook/Pricing History/pricing_history.csv")

with open(pricing_file, 'a', newline='') as fp:
    a = csv.writer(fp, delimiter=',')
    data = [[datetime.now(),
             URL,
             price_ebook,
             price_book,
             price_rrp_ebook,
             price_rrp_book]]
    a.writerows(data)

# Tell me when we're finished
print("Pricing data obtained!")