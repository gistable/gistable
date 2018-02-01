import requests

def getRate(base,to):
	
	''' converts currency using api for further information visit http://fixer.io/'''
	
	api = "http://api.fixer.io/latest?base="+base
	data =  requests.get(api)
	jsonData = data.json()
	for key,value in jsonData.iteritems():
		if key=="rates":
			for countryCode,rate in value.iteritems(): 
				if countryCode==to:
					return float(rate)

def euroToUsd(amount):
	
	''' converts Euro to USD '''
	
	return getRate("EUR","USD")*amount

def usdToEuro(amount):
	
	''' converts USD to Euro '''
	
	return getRate("USD","EUR")*amount

if __name__=="__main__":
	print euroToUsd(10)
	print usdToEuro(10)
 	