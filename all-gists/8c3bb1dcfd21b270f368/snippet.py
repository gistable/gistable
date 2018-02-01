#! /usr/bin/python
# coding=utf-8

import cgi
import cgitb
cgitb.enable()

from datetime import datetime, timedelta
import json
import os
import re
import tempfile
import time
import urllib2

futureRE ='id="Future_branch_dates".*(<table.*</table>).*id="Past_branch_dates"' 
pastRE ='id="Past_branch_dates".*(<table.*</table>).*class="printfooter"' 
dataRE = '<t[hd]>(.*?)</t[hd]>'

def strip(values):
  return [x.strip() for x in values]

def getHeaders(data):
  headers = strip(re.findall(dataRE, data[0], re.DOTALL))
  headers = [x.lower() for x in headers]
  return headers, data[1:]

def mungeData(data, past):
  if not data['merge date'] or not data['aurora']:
    return None
  rv = {
    'sDate': data['merge date'].replace("*", ""),
    'sTime': data['merge date'][5:10].replace("-", ":"), 
    'sDeparture': data['aurora'],
    'nStatus': 2,
    'nTrack': data['merge date'][2:4],
    'bLight': True,
    'data': data
  }
  if past:
    rv['nStatus'] = 4
    rv['bLight'] = False
  return rv

def headerizeData(headers, data, past):
  rv = []
  for line in data:
    values = strip(re.findall(dataRE, line, re.DOTALL))
    temp = {}
    if len(values) != len(headers):
      continue
    for i,value in enumerate(values):
      temp[headers[i]] = value
    rv.append(mungeData(temp, past));
    if not past and len(rv) == 1:
      rv[0]['nStatus'] = 1
  while None in rv:
    rv.remove(None)
  return rv

def addArrivalTimes(data):
  for item in data:
    mergeDate = datetime.strptime(item['sDate'], "%Y-%m-%d").date()
    releaseDate = [x for x in data if x['data']['release'] == item['sDeparture']]
    if len(releaseDate):
      releaseDate = releaseDate[0]['data']['release date'].replace("*", "")
    else:
      releaseDate = mergeDate + timedelta(weeks=2*6) + timedelta(days=1)
    item['sDeparture'] += "   (" + str(releaseDate) + ")"
  return data

def main():
  tempname = os.path.join(tempfile.gettempdir(), 'releasedata.json')
  oneDay = 1L * 24 * 60 * 60
  if os.path.exists(tempname) and os.path.getmtime(tempname) < (time.time() + oneDay):
    print "Content-Type: application/json"
    print "Access-Control-Allow-Origin: *\n"
    output = open(tempname, 'rb').read()
    print output
    return
  
  x = urllib2.urlopen("https://wiki.mozilla.org/RapidRelease/Calendar")

  data = x.read().decode('utf-8');
  releases = re.search(futureRE, data, re.DOTALL).groups()[0]
  z = strip(re.findall('<tr>(.*?)</tr>', releases, re.DOTALL))
  headers, z = getHeaders(z)
  rv = headerizeData(headers, z, False)

  releases = re.search(pastRE, data, re.DOTALL).groups()[0]
  z = strip(re.findall('<tr>(.*?)</tr>', releases, re.DOTALL))
  headers, z = getHeaders(z)
  rv += headerizeData(headers, z, True)
  rv.sort(key=lambda value: value['data']['release date'])

  addArrivalTimes(rv)

  print "Content-Type: application/json"
  print "Access-Control-Allow-Origin: *\n"
  output = json.dumps(rv).encode('utf-8')
  print output
  open(tempname, 'wb').write(output)

if __name__ == "__main__":
  main()
