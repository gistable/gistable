#Connects to the Socrata search API and loads data describing the tabular datasets in the catalog for use by D3 tree map
#This version connects to a list of existing Socrata instances and loops through the ones categorized as city
#Use: python dataportalapi.py > portaldata.json

import requests, json, math, re

def check_categories(d,category):
  for i in range(len(d)):
    if d[i]['name'] == category: return i
  return -1
#TODO: load via standard csv file with Name, URL, Scale, and Catalog Type as fields
c = requests.get("https://opendata.socrata.com/resource/6wk3-4ija.json?$where=type='city'")
cities = c.json()

final = {"name" : "Socrata Data Portals", "children": []}

for city in cities:
	#sURL = 'http://nycopendata.socrata.com'
	sURL = city['open_data_site_url']['url'].strip('/')
	out = []
	page = 1
	records = 0
	total = 2
	rwithdata = 0
	while records < total:
		payload = {'limit' : 100, 'page' : page, 'limitTo' : 'TABLES'}
		r = requests.get(sURL + '/api/search/views.json', params=payload)

		responses = r.json()
		total = responses['count']
		#had to add this check as nycopendata is somehow returning fewer results than it indicated in count
		if 'results' in responses:
			for response in responses['results']:
				view = response['view']
				records += 1
				if len(view['columns']) != 0 and 'cachedContents' in view['columns'][0] and 'flags' in view:
					#print view['flags']
					rwithdata += 1
					name = view['name']
					vid = view['id']
					views = view['viewCount']
					size = view['columns'][0]['cachedContents']['non_null']
					if size == 0:
						size = 2 #probably should just skip these altogether, for now making them a tiny dataset so LOG(0) doesn't occur
					logsize = math.log(size)
					if 'category' in view:
						category = view['category']
					else:
						category = "No Category"
					if 'tags' in view:
						for tag in view['tags']:
							#tags aren't used in the json file yet, these could probably be used to do alternate visualizations or in a companion list, this is just a placeholder for now
							foo = tag
					index = check_categories(out,category)
					url = sURL + '/d/' + vid
					if index == -1:
						out.append({"name": category, "children": [ {"name": name, "value": logsize, "url": url, "size": logsize } ] })
					else:
						out[index]["children"].append({"name": name, "value": logsize, "url": url, "size": logsize })
		else:
			records = total
		page += 1
	portaldata = {"name" : city['customer_name'] + " Data Portal", "count" : rwithdata, "children" : out}
	final["children"].append(portaldata)
print json.dumps(final)