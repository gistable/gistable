from boto.route53.connection import Route53Connection

# your amazon keys
key = ""
access = ""

if __name__ == '__main__':
    zones = {}
    route53 = Route53Connection(key, access)
    
    # create a new zone
    response = route53.create_hosted_zone('example.com')
    
    # list existing hosted zones
    results = route53.get_all_hosted_zones()
    for zone in results['ListHostedZonesResponse']['HostedZones']:
        print "========================================"
        print zone['Name']
        print "\t%s" % zone['Id']
        zone_id = zone['Id'].replace('/hostedzone/', '')
        zones[zone['Name']] = zone_id
        sets = route53.get_all_rrsets(zone_id)
        for rset in sets:
            print "\t%s: %s %s @ %s" % (rset.name, rset.type, rset.resource_records, rset.ttl)
    
    # add an A record
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <ChangeResourceRecordSetsRequest xmlns="https://route53.amazonaws.com/doc/2010-10-01/">
        <ChangeBatch>
            <Comment>Add record</Comment>
            <Changes>
                <Change>
                    <Action>CREATE</Action>
                    <ResourceRecordSet>
                        <Name>%s.</Name>
                        <Type>A</Type>
                        <TTL>7200</TTL>
                        <ResourceRecords>
                            <ResourceRecord>
                                <Value>%s</Value>
                            </ResourceRecord>
                        </ResourceRecords>
                    </ResourceRecordSet>
                </Change>
            </Changes>
        </ChangeBatch>
    </ChangeResourceRecordSetsRequest>""" % ("example.com", "127.0.0.1")
    response = route53.change_rrsets(zones['example.com'], xml)

    # add an MX record
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <ChangeResourceRecordSetsRequest xmlns="https://route53.amazonaws.com/doc/2010-10-01/">
        <ChangeBatch>
            <Comment>Add record</Comment>
            <Changes>
                <Change>
                    <Action>CREATE</Action>
                    <ResourceRecordSet>
                        <Name>%s.</Name>
                        <Type>MX</Type>
                        <TTL>7200</TTL>
                        <ResourceRecords>
                            <ResourceRecord>
                                <Value>%s</Value>
                            </ResourceRecord>
                        </ResourceRecords>
                    </ResourceRecordSet>
                </Change>
            </Changes>
        </ChangeBatch>
    </ChangeResourceRecordSetsRequest>""" % ("example.com", "10 mx.example.com")
    response = route53.change_rrsets(zones['example.com'], xml)

