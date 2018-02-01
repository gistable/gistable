import requests, json
from time import sleep

def getBitcoinPrice():
    URL = 'https://www.bitstamp.net/api/ticker/'
    try:
        r = requests.get(URL)
        priceFloat = float(json.loads(r.text)['last'])
        return priceFloat
    except requests.ConnectionError:
        print "Error querying Bitstamp API"

while True:
	print "Bitstamp last price: $" + str(getBitcoinPrice()) + "/BTC"
	sleep(5) 