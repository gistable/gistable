import ast
import datetime
import json
import sys
import requests
import urllib
from tabulate import tabulate

url = "https://www.whatruns.com/api/v1/get_site_apps"
data = {"data": {"hostname": sys.argv[1], "url": sys.argv[1],
        "rawhostname": sys.argv[1]}}
data = urllib.urlencode({k: json.dumps(v) for k, v in data.iteritems()})
data = data.replace('+', '')
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
response = requests.post(url, data=data, headers=headers)
loaded = json.loads(response.content)
apps = ast.literal_eval(loaded['apps'])
nuance = apps.keys().pop()

entries = list()
for app_type, values in apps[nuance].iteritems():
    for item in values:
        dt = datetime.datetime.fromtimestamp((item['detectedTime']/1000))
        ldt = datetime.datetime.fromtimestamp((item['latestDetectedTime']/1000))
        entries.append({'Type': app_type, 'Name': item['name'],
                        'Detected': dt, 'Last_Detected': ldt})

print tabulate(entries, headers='keys')
