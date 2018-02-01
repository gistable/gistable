import requests
import csv
from datetime import timedelta
import dateutil.parser
import time


i=0
sleep = 15

# Change the range depending on how long you like to record the data
for i in range (0,50):
    try:
        url="https://rata.digitraffic.fi/api/v1/train-locations/latest?bbox=20,60,33,70"
        r = requests.get(url, timeout=3)
        j = r.json() 
        
        for each in j:
            t = dateutil.parser.parse(each['timestamp']) + timedelta(hours=2)
            formt='{:%Y-%m-%d %H:%M:%S}'.format(t)
            values = each['trainNumber'], formt, each['speed'], each['location']['coordinates'][0], each['location']['coordinates'][1]
            with open(r'train_points.csv', 'a') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_NONE, lineterminator='\n')
                writer.writerow(values)
                
# This is here so that the code won't fail if URL doesn't respond  
    except:
        print('URL not responding')
    
# Add to range, print where the request is and wait for next request
    i+=1
    print('Completed request number ' + str(i))
    time.sleep(sleep)