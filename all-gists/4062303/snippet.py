import json
import urllib2

r = urllib2.urlopen("http://blockchain.info/charts/trade-volume?timespan=all&format=json")
tradevol_string = r.read()
r.close()

r = urllib2.urlopen("http://blockchain.info/charts/estimated-transaction-volume-usd?timespan=all&format=json")
txvol_string = r.read()
r.close

r = urllib2.urlopen("http://blockchain.info/charts/market-price?timespan=all&format=json")
price_string = r.read()
r.close

tradevol_dict = json.loads(tradevol_string)
txvol_dict = json.loads(txvol_string)
price_dict = json.loads(price_string)

tradevol_list = tradevol_dict["values"]
txvol_list = txvol_dict["values"]
price_list = price_dict["values"]

s = "Day,Price,Trade Volume,TX Volume,Ratio"
print s
for i in range(0,1400):
	tv = tradevol_list[i]["y"]
	txv = txvol_list[i]["y"]
	p = price_list[i]["y"]
	if tv > 0:
		s = repr(i) + "," + repr(p) + "," + repr(tv) + "," + repr(txv) + "," + repr(txv/tv)
	else:
		s = repr(i) + "," + repr(tv) + "," + repr(txv) + "," + "0"
	print s