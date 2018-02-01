#!/opt/local/bin/python

import httplib, json

APIKEY = "YOUR_API_KEY_HERE"

headers = {"TekSavvy-APIKey": APIKEY}
conn = httplib.HTTPSConnection("api.teksavvy.com")
conn.request('GET', '/web/Usage/UsageSummaryRecords?$filter=IsCurrent%20eq%20true', '', headers)
response = conn.getresponse()
jsonData = response.read()

data = json.loads(jsonData)

pd  = data["value"][0]["OnPeakDownload"]
pu  = data["value"][0]["OnPeakUpload"]
opd = data["value"][0]["OffPeakDownload"]
opu = data["value"][0]["OffPeakUpload"]
sd  = data["value"][0]["StartDate"]
ed  = data["value"][0]["EndDate"]

print "%s %s %s %s" % (pd, pu, opd, opu)