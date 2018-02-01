import simplejson as json
import requests

#your spreadsheet key here. I'm using an example from the Victorian election campaign

key = "1THJ6MgfEk-1egiPFeDuvs4qEi02xTpz4fq9RtO7GijQ"

#google api request urls - I'm doing the first one just to get nice key values (there's probably a better way to do this)

url1 = "https://spreadsheets.google.com/feeds/cells/" + key + "/od6/public/values?alt=json"
url2 = "https://spreadsheets.google.com/feeds/list/" + key + "/od6/public/values?alt=json"

#get the json in cell format from google

ssContent1 = requests.get(url1).json()

#lists to store new keys and data

newKeys = []
newData = []

#make a list of the entries in the first row for nice keys

for item in ssContent1['feed']['entry']:
	if item['gs$cell']['row'] == '1':
		newKeys.append(item['content']['$t'])

print newKeys

#get json in list format 

ssContent2 = requests.get(url2).json()

#remap entries from having gsx$-prefixed keys to having no prefix, ie our first row as keys

for entry in ssContent2['feed']['entry']:
	rowData = []
	for key in newKeys:
		rowData.append(entry['gsx$' + key]['$t'])
	newData.append(dict(zip(newKeys, rowData)))

#print newData

#make it into a json object for writing to file or s3

newJson = json.dumps(newData)	

print newJson

#saves the json file locally as output.json. you could do other stuff with it though, like put it on a server somewhere 

with open('output.json','w') as fileOut:
		fileOut.write(newJson)