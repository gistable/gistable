from boto.route53.connection import Route53Connection
import urllib2
from syslog import syslog

# ======= CONFIG ========
AWS_ACCESS_KEY_ID = 'XXXXXXXXXXXXXXXXXX'
AWS_SECRET_ACCESS_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXX'
DDNSNAME = "foo.example.com." # Should end in period
ZONEID = "XXXXXXXXX"
# ===== END CONFIG ======

def wtf_myip():
    ip = urllib2.urlopen("http://wtfismyip.com/text").read().strip()
    return ip

def update_route53():
    route53 = Route53Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    rr = route53.get_all_rrsets(ZONEID)
    oldips = []
    for r in rr:
        #print r.name
        if r.name == DDNSNAME:
            oldips += r.resource_records
    deletechanges = ""
    newip = wtf_myip()
    if oldips == [newip]:
        #No need to update!!!
        syslog("Record in route53 matches current ip")
    else:
        for ip in oldips:
            deletechanges += """
                        <Change>
                    <Action>DELETE</Action>
                    <ResourceRecordSet>
                        <Name>%s</Name>
                        <Type>A</Type>
                        <TTL>60</TTL>
                        <ResourceRecords>
                            <ResourceRecord>
                                <Value>%s</Value>
                            </ResourceRecord>
                        </ResourceRecords>
                    </ResourceRecordSet>
                </Change>
    """ %(DDNSNAME, ip)
        #print deletechanges
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<ChangeResourceRecordSetsRequest xmlns="https://route53.amazonaws.com/doc/2011-05-05/">
    <ChangeBatch>
        <Comment>Add record</Comment>
        <Changes>
            %s
            <Change>
                <Action>CREATE</Action>
                <ResourceRecordSet>
                    <Name>%s</Name>
                    <Type>A</Type>
                    <TTL>60</TTL>
                    <ResourceRecords>
                        <ResourceRecord>
                            <Value>%s</Value>
                        </ResourceRecord>
                    </ResourceRecords>
                </ResourceRecordSet>
            </Change>
        </Changes>
    </ChangeBatch>
</ChangeResourceRecordSetsRequest>""" % (deletechanges, DDNSNAME, newip)
        #print xml
        c = route53.change_rrsets(ZONEID,xml)
        syslog(c["ChangeResourceRecordSetsResponse"]["ChangeInfo"]["Id"].replace("/change/", ""))



if __name__ == "__main__":
    update_route53()
