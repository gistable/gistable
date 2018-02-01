#!/usr/bin/python

# Daniel De Marco - ddm@didiemme.net - 2012-02-23

# suds from https://fedorahosted.org/suds/
import suds
import sys


def get_warr(svctag):
        # url = "http://xserv.dell.com/services/assetservice.asmx?WSDL"
        url = "http://143.166.84.118/services/assetservice.asmx?WSDL"
        client = suds.client.Client(url)
        res=client.service.GetAssetInformation('12345678-1234-1234-1234-123456789012', 'dellwarrantycheck', svctag)

        #print client
        #print client.dict(res)

        asset=res['Asset'][0]

        hdrdata=asset['AssetHeaderData']
        if 'Entitlements' in asset:
                ent=asset['Entitlements'][0]
        else:
                ent=[]

        shipped=hdrdata['SystemShipDate']
        warrs=[]
        for i in ent:
                if i==None:
                        continue
                if i['ServiceLevelDescription'] == 'P, Dell Digitial Delivery':
                        continue
                warrs.append(i['EndDate'])

        if warrs:
                warrs.sort()
                endwarranty=warrs[-1]
                return (shipped.strftime("%Y-%m-%d"), endwarranty.strftime("%Y-%m-%d"))
        else:
                return (shipped.strftime("%Y-%m-%d"), "0000-00-00")


if __name__ == "__main__":
        if len(sys.argv) != 2:
                raise RuntimeError("usage: %s SERVICETAG" % sys.argv[0])
        (shipped, endw)=get_warr(sys.argv[1])
        print 'shipped:      ', shipped
        print 'end warranty: ', endw

