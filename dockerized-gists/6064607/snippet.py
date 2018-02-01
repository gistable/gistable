#!/usr/bin/python
 
# Daniel De Marco - ddm@didiemme.net - 2012-02-23 
 
# suds from https://fedorahosted.org/suds/
import suds
import sys

tags = [
   { 'name': 'HOSTNAME_1', 'tag': 'TAG_ID_1' },
   { 'name': 'HOSTNAME_2', 'tag': 'TAG_ID_2' },
]

def get_warr(tags):
       url = "http://143.166.84.118/services/assetservice.asmx?WSDL"
       client = suds.client.Client(url)

       for tag in tags:
           res=client.service.GetAssetInformation('12345678-1234-1234-1234-123456789012', 'dellwarrantycheck', tag['tag'])

           #print client.dict(res)

           hdrdata=res['Asset'][0]['AssetHeaderData']
           ent=res['Asset'][0]['Entitlements'][0]

           shipped=hdrdata['SystemShipDate']
           warrs=[]
           for i in ent:
                   if i==None:
                           continue
                   warrs.append(i['EndDate'])

           warrs.sort()
           endwarranty=warrs[-1]
           print 'server: %s\ntag: %s\nshipped: %s\nwarranty expires: %s' % (tag['name'], tag['tag'], shipped.strftime("%Y-%m-%d"), endwarranty.strftime("%Y-%m-%d"))
           print '*' * 50

if __name__ == "__main__":
   get_warr(tags)