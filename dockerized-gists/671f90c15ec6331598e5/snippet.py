#! /usr/bin/env python

import json
import requests

def process(obj, ds):
	data = {}
	values  =  obj[ds]['value']
	index = obj[ds]['dimension'][obj[ds]['dimension']['id'][1]]['category']['index']
	labels = obj[ds]['dimension'][obj[ds]['dimension']['id'][1]]['category']['label']
	for l in labels:
		num = index[l]
		count = values[str(num)]
		data[labels[l]] = count
	return data


def getdata(dataset, geog_code):
	baseurl = "http://data.ons.gov.uk/ons/api/data/dataset/"
	payload = {'apikey': apikey, 'context': 'Census', 'geog' : '2011WARDH', 'dm/2011WARDH' : geog_code, 'totals' : 'false', 'jsontype' : 'json-stat' }
	r = requests.get(baseurl+"/"+dataset+".json", params=payload)
	obj = json.loads(r.text)
	return obj
	

apikey = "XXXXXXXX"

dataset = "QS104EW" # Gender Split
geog_code = "K04000001" #England & Wales

jsonstat = getdata(dataset, geog_code)
process(jsonstat, dataset)


