# -*- coding: utf-8 -*-
import requests
import json
from datetime import datetime
import csv
import time

class scraping:

    def __init__(self):
        #self.last_touched = (raw_input('enter unix timestamp where you left off:'))
        #print self.last_touched
        self.output_file = csv.writer(open('venmo_output.csv', 'a'))

    def get_unix(self,timestamp):
        a = timestamp
        print a
        return a

    def pull_data(self):
        try:
            URL = "https://venmo.com/api/v5/public"
            return json.loads(requests.get(URL).text)
        except (requests.exceptions.ConnectionError,ValueError) as e:
            return None

    def transform_data(self,json_object):
        output_array = []
        try:
            json_array = json_object['data']
            for item in json_array:
                try:
                    output_array.append([item['story_id'],item['updated_time'],item['actor']['name'],
                        item['actor']['picture'],item['actor']['id'],
                        item['transactions'][0]['target']['name'],
                        item['transactions'][0]['target']['picture'],
                        item['transactions'][0]['target']['id'],
                        item['message'],item['type']])
                except TypeError:
                    pass
        except (TypeError, KeyError) as e:
            pass
        return output_array

    def write_data(self,raw_array):
        for row in raw_array:
            if row[1] > self.last_touched:
                self.last_touched = row[1]
                self.output_file.writerow([unicode(s).encode("utf-8") for s in row])

if __name__ == '__main__':
    instance = scraping()
    while True:
        start_time = int(time.time())
        json_object = instance.pull_data()
        raw_array = instance.transform_data(json_object)
        instance.write_data(raw_array)
        end_time = int(time.time())
        if end_time - start_time > 10:
            pass
        else:
            time.sleep(10 - (end_time-start_time))