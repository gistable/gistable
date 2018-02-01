import requests
import csv
import datetime
import calendar
import time
            
i=0
# Change the range depending on how long you like to record the data
for i in range (0,50):
    
# Set up the request. Get all locations since last request.
    url = 'http://meri-test.digitraffic.fi/api/v1/locations/latest?from='
    sleep = 15
    start = (calendar.timegm(time.gmtime()) - sleep) * 1000
    
# Do the request and read the response
    try:
        r = requests.get(url + str(start))
        j = r.json() 
        
# Go through all the features in the response, format timestamp properly and write to csv
        for each in j['features']:
            epoch = (each['properties']['timestampExternal']) / 1000
            timestamp = datetime.datetime.utcfromtimestamp(epoch)
            t='{:%Y-%m-%d %H:%M:%S}'.format(timestamp)
            values = each['mmsi'], each['geometry']['coordinates'][0], each['geometry']['coordinates'][1], t
            with open(r'ships.csv', 'a') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_NONE, lineterminator='\n')
                writer.writerow(values)
                
# This is here so that the code won't fail if URL doesn't respond  
    except:
        print('URL not responding')
    
# Add to range, print where the request is and wait for next request
    i+=1
    print(i)
    time.sleep(sleep)