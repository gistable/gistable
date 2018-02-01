# We need to specify our api key here to use in the request
apikey = "XXXXXX"

#Now we'll setup the base url for the ons API
baseurl = "http://data.ons.gov.uk/ons/api/data/dataset/"

# We need to specify the dataset we are after, in this case its just the split of gender
dataset = "QS104EW" 

#And pass in some of our parameters

payload = {'apikey': apikey,  #our API Key from earlier
            'context': 'Census', # We're looking at the census data
            'geog' : '2011WARDH', # Using the 2011 Administrative Hieracry
            'dm/2011WARDH' : 'K04000001', # And the geography code here is for all of England and Wales
            'totals' : 'false', # We're only looking at one area so we don't care about totals
            'jsontype' : 'json-stat' } # And we need to specify that we want the JSON-STAT output


r = requests.get(baseurl+"/"+dataset+".json", params=payload)  # Now we  make the request

obj = json.loads(r.text) #  we take the response data and parse it as JSON to load into an object.