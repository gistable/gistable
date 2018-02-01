import urllib2
import json

data = urllib2.urlopen("http://api.bitcoincharts.com/v1/weighted_prices.json")

def convert_to_bitcoin(amount, currency):
    bitcoins = json.loads(data.read())
    converted = float(bitcoins[currency]["24h"]) * amount
    print converted


convert_to_bitcoin(1, "USD")
