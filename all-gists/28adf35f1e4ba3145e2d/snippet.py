# /usr/bin/python3.4
# -*- coding: utf-8 -*-
__author__ = 'Mertcan Gökgöz'

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request


def DolarParse():
    pasteURL = "http://tr.investing.com/currencies/usd-try"
    data = urlopen(Request(pasteURL, headers={'User-Agent': 'Mozilla'})).read()
    parse = BeautifulSoup(data)
    for dolar in parse.find_all('span', id="last_last"):
        liste = list(dolar)
        print("Güncel Dolar Kuru: " + str(liste))


def EuroParse():
    pasteURL = "http://tr.investing.com/currencies/eur-try"
    data = urlopen(Request(pasteURL, headers={'User-Agent': 'Mozilla'})).read()
    parse = BeautifulSoup(data)
    for dolar in parse.find_all('span', id="last_last"):
        liste = list(dolar)
        print("Güncel Euro Kuru: " + str(liste))


DolarParse()
EuroParse()