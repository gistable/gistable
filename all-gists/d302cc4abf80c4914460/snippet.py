#!/usr/bin/python

import httplib
import json
import csv
import os
import sys
import time
import urllib
import datetime

APPLICATION_ID = "" #APP Key
REST_API_KEY = "" #REST API Key
MASTER_KEY = "" #Master Key
CLASSES = "TableName" #Enter comma seperated classnames here, ex "User,Role" etc! Don't add space after/before comma.

def getData(app_id, rest_api_key, api_endpoint, master_key=None, limit=1000, order=None, skip=None, filter_json=None, api_version=1):
    con = httplib.HTTPSConnection('api.parse.com', 443)
    con.connect()

    header_dict = {'X-Parse-Application-Id': app_id,
                   'X-Parse-REST-API-Key': rest_api_key
                   }

    if master_key is not None:
        header_dict['X-Parse-Master-Key'] = master_key

    params_dict = {}
    if order is not None:
        params_dict['order'] = order
    if limit is not None:
        params_dict['limit'] = limit
    if skip is not None:
        params_dict['skip'] = skip
    if filter_json is not None:
        params_dict['where'] = filter_json

    params = urllib.urlencode(params_dict)
    con.request('GET', '/%s/%s?%s' % (api_version, api_endpoint, params), '', header_dict)

    try:
        response = json.loads(con.getresponse().read())
    except Exception, e:
        response = None
        raise e

    return response

def main():
    print "*** Requesting...  ***\n"

    class_list = CLASSES.split(",") #For multiple classes!
    DEFAULT_CLASSES = {'User': 'users', 'Role': 'roles', 'File': 'files', 'Events': 'events', 'Installation': 'installations'}

    json_file_path = os.getcwd()

    for classname in class_list:
        results = {'results': []}
        object_count = 0
        skip_count = 0
        skip = 0
        limit = 10

        if classname not in DEFAULT_CLASSES.keys():
            endpoint = '%s/%s' % ('classes', classname)
        else:
            endpoint = DEFAULT_CLASSES[classname]

        sys.stdout.write(' Fetching %s table data - ' % classname)
        sys.stdout.flush()

        while True:
            startTimer = time.clock()
	          skip = skip_count*limit #Increment for skip
	    
            response = getData(APPLICATION_ID, REST_API_KEY, endpoint, master_key=MASTER_KEY, limit = limit, skip = skip)

            if 'results' in response.keys() and len(response['results']) > 1:
                object_count += len(response['results'])
                skip_count = skip_count+1
                results['results'].extend(response['results'])
            else:
                parse_done = time.clock() - startTimer
                print ' Got: %.4f records in %.4f secs\n' % (object_count, parse_done)
                break

        with open(os.path.join(json_file_path, '%s.json' % classname), 'w') as json_file:
            json_file.write(json.dumps(results, indent=4, separators=(',', ': ')))

        print 'Generating csv... '

        with open(os.path.join(json_file_path, '%s.json' % classname), 'r') as json_file:
            
            data = json.load(json_file)
            f = csv.writer(open(os.path.join(json_file_path, '%s.csv' % classname), 'w'))
            #f.writerow(["objectId", "store", "messageType", "sentFrom", "createdAt"]) <- Uncomment to manually set column titles & sequence
            f.writerow(data["results"][0].keys())
            for x in data["results"]:
                # Uncomment below line to manually set sequence if you know column titles.
                #f.writerow([x["objectId"], x["store"], x["messageType"], x["sentFrom"], dateutil.parser.parse(x["createdAt"]).strftime("%d-%b-%Y, %H:%M:%S")]) 
                f.writerow(x.values())
            print " CSV Generated... \n"

if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        raise e