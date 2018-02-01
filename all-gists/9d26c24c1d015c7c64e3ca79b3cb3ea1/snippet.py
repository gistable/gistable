#! /usr/bin/python

#Simple script for importing data from bitly to yourls using  bitly and yourls API.
import urllib2, json, urllib

#Add the following data
yourls_host = 'your-domain-where-yours-is-installed.com'
bitly_token = 'your-bitly-token'
yourls_signature = 'your-yourls-signature-key'

def pushto_yourls_api(data):
    url_dest = 'http://'+yourls_host+'/yourls-api.php'
    for x in data['data']['link_history']:
        link = x['link'].split('/')[3]
        long_url = x['long_url']
        values = dict(action='shorturl', url = long_url, keyword = link , signature=yourls_signature)
        req_data = urllib.urlencode(values)
        req = urllib2.Request(url_dest, req_data)
        rsp = urllib2.urlopen(req)
        content = rsp.read()
        print content



origen_url = 'https://api-ssl.bitly.com/v3/user/link_history?format=json&amp;amp;access_token='+bitly_token+'&amp;amp;limit=50'
bitly_result = True
offset = 0

while bitly_result:    
    url = origen_url + '&amp;amp;offset=' + str(offset)
    print url    
    response = urllib.urlopen(url)
    data = json.loads(response.read())    
    if len(data['data']['link_history']) &amp;lt; 50:
       bitly_result = False  
    offset +=50
    pushto_yourls_api(data)