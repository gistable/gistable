#!/usr/bin/env python
import boto
from boto.route53.record import ResourceRecordSets
import logging

conn = boto.connect_ec2()
DNS_EXCLUSION_TAG = 'ExcludeFromDNS'   # If this tag exists on an instance, no DNS values will be populated
DNS_TAGS = ['ShortName', 'Name']       # This is the list of instance tags we want to populate DNS entries from
DNS_SUFFIX = 'YOUR_SUBDOMAIN_HERE'     # Suffix under which to create DNS records
ROUTE53_ZONE_ID = 'YOUR_ZONE_ID_HERE'  # The zone id from route53 of the zone we will be adding these entries under
LOG_PATH = '/usr/local/scripts/populate_dns_records.log'
logging.basicConfig(filename=LOG_PATH, level=logging.WARNING, format='%(asctime)s %(module)s %(message)s')

def add_cname(instance, hostname):
    conn = boto.connect_route53()
    existing_entries = conn.get_all_rrsets(ROUTE53_ZONE_ID)

    changes = ResourceRecordSets(conn, ROUTE53_ZONE_ID)
    for item in existing_entries:
        # Move to the next entry if we do not match
        if item.name != hostname and item.name != "CNAME" and item.ttl != 60:
            continue

        # If we have nothing to change, return
        if instance.dns_name in item.resource_records:
            logging.info("Nothing to change for %s", hostname)
            return

        # We're a record that needs updating, delete the existing entry, so we can re-add it
        for record in item.resource_records:
            logging.warning("Deleting CNAME {0}/{1}".format(hostname, record))
            change = changes.add_change("DELETE", hostname, "CNAME", ttl=60) # Change this at some point to ttl=item.ttl, leaving it hard set so we don't overwrite anything  entered by hand
            change.add_value(record)

    # We either don't exist or need to update our existing entry (its already been deleted)
    logging.warning("Adding CNAME entry for %s to %s", hostname, instance.dns_name)
    change = changes.add_change("CREATE", hostname, "CNAME", ttl=60)
    change.add_value(instance.dns_name)

    try:
        changes.commit()
    except Exception, e:
        logging.error(e)

if __name__ == '__main__':
    reservations = conn.get_all_instances()
    entries_to_make = {}

    for reservation in reservations:
        instances = reservation.instances

        for instance in instances:
            if instance.tags.get(DNS_EXCLUSION_TAG, None):
                logging.info("Skipping {0}" .format(instance.id) )
                continue

            hostnames = set()
            hostnames.add(instance.id + ".ec2" + DNS_SUFFIX)

            for tag in DNS_TAGS:
                tag_value = instance.tags.get(tag, None)

                if tag_value is not None:
                    hostname = tag_value + DNS_SUFFIX
                
                tag_value = instance.tags.get(tag, None)
                if tag_value is not None:
                    hostname = tag_value + DNS_SUFFIX
                    hostnames.add(hostname)

            for hostname in hostnames:
                add_cname(instance, hostname)