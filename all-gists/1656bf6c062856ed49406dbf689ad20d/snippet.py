import json
import requests
from dateutil.parser import parse
from dateutil.parser import parserinfo
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup


def getNewsFromFinViz(ticker):
	r = requests.get('http://finviz.com/quote.ashx?t=' + ticker)
	if(r.status_code != 200):
		return
	return processRequest(r.text)


def processRequest(htmlText):
	currentDate = datetime.now() #- timedelta(days=1)  # to remove a certain time from current time
	perfectSoup = BeautifulSoup(htmlText, 'html.parser')
	table = perfectSoup.find_all('table', {"id": "news-table"})[0] # find the first table that has the news 
	for row in table.find_all('tr'):
		for column in row.find_all('td'):
			#if there are no link tags (a href) here then this must be a date
			if(column.a is None):
				date = parse(column.text)
				# if the column contains a month and the date is the same as today's date then print out the results
				if(column.text.find(date.strftime("%B")[0:3]) != -1):
					print(date.strftime("%B, %d %Y"))
					print("{0}{1}".format("\t", date.strftime("%I:%M%p")), end='')
				else: # the column text does not contain a month (belongs to the same day as the previous link)
					print("{0}{1}".format("\t", column.text), end='')
			else:
				print("{0}{1}".format("\t\t", column.a['href']))


#test
getNewsFromFinViz("JPM")
