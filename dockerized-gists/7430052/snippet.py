# search for available tickets at stubhub.com
# and place the result into csv file

import sys
import requests
import json
import csv
from time import time

# input data
#EVENT ID FROM STUBHUB.COM
event = '4360923'

tickets_list = []
t = int(time())

csvfile = 'elton.csv'
csvfields = ['location', 'row', 'qty', 'price']
url = 'http://www.stubhub.com/ticketAPI/restSvc/event/' + event + '/sort/price/0?ts=' + str(t) + '000'

# make get request to stubhub.com and take the result in json
response = requests.get(url)
response_dict = response.json()
tickets = response_dict['eventTicketListing']['eventTicket']

# select location, row, quantity and price of the tickets
for ticket in tickets:
	d = {}
	d['location'] = ticket['va']
	d['row'] = ticket['rd']
	d['qty'] = ticket['qt']
	d['price'] = ticket['cp']
	tickets_list.append(d)

# write result into csv file
with open(csvfile, 'wb') as f:
	d_writer = csv.DictWriter(f, csvfields)
	d_writer.writer.writerow(csvfields)
	d_writer.writerows(tickets_list)
