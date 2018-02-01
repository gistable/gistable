"""
 Requeriments:

     $ sudo pip install boto dnspython

 Edit ~/.boto to use your AWS credentials

"""
import time
import sys
import urllib2
import dns.resolver
from boto.route53.connection import Route53Connection
from boto.route53.exception import DNSServerError
from boto.route53.record import ResourceRecordSets
import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler('dyndns_route53.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler) 
logger.setLevel(logging.INFO)

# Settings, Change me!
HOSTED_ZONE = 'ZXQU10000001'
DOMAIN_NAME = 'home.mydomain.com'


get_change_id = lambda response: response['ChangeInfo']['Id'].split('/')[-1]
get_change_status = lambda response: response['ChangeInfo']['Status']

def resolve_name_ip(name):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [
        '8.8.8.8',
        '8.8.4.4'
    ]
    answer = resolver.query(name)
    
    """
    >>> answer.response.answer[0].to_text()
    home.mydomain.com. 60 IN A 192.168.0.2'
    >>> answer.response.answer[0].items
    [<DNS IN A rdata: 192.168.0.2>]
    >>> answer.response.answer[0].items[0].address
    '192.168.0.2'
    """
    return answer.response.answer[0].items[0].address
    
def main():
    
    # Get your ip using a public service
    current_ip = urllib2.urlopen('http://ip.42.pl/raw').read()

    # Avoid to hit the Route53 API if is not necessary.
    # so compare first to a DNS server if the IP changed
    resolved_ip = resolve_name_ip(DOMAIN_NAME)
    if resolved_ip == current_ip:
        logger.debug('DNS response (%s) and public IP (%s) are the same, nothing to do' % (resolved_ip, current_ip))
        return
    
    conn = Route53Connection()

    try:
        zone = conn.get_hosted_zone(HOSTED_ZONE)
    except DNSServerError:
        logger.error('%s Zone Not Found' % HOSTED_ZONE)
        sys.exit(1)

    response = conn.get_all_rrsets(HOSTED_ZONE, 'A', DOMAIN_NAME, maxitems=1)[0]
    
    if current_ip not in response.resource_records:
        logger.info('Found new IP: %s' % current_ip)

        # Delete the old record, and create a new one.
        # This code is from route53.py script, the change record command
        changes = ResourceRecordSets(conn, HOSTED_ZONE, '')
        change1 = changes.add_change("DELETE", DOMAIN_NAME, 'A', response.ttl)
        for old_value in response.resource_records:
            change1.add_value(old_value)
        change2 = changes.add_change("CREATE", DOMAIN_NAME, 'A', response.ttl)
        change2.add_value(current_ip)

        try:
            commit = changes.commit()
            logger.debug('%s' % commit)
        except:
            logger.error("Changes can't be made: %s" % commit)
            sys.exit(1)
        else:
            
            change = conn.get_change(get_change_id(commit['ChangeResourceRecordSetsResponse']))
            logger.debug('%s' % change)

            while get_change_status(change['GetChangeResponse']) == 'PENDING':
                time.sleep(2)
                change = conn.get_change(get_change_id(change['GetChangeResponse']))
                logger.debug('%s' % change)                
            if get_change_status(change['GetChangeResponse']) == 'INSYNC':
                logger.info('Change %s A de %s -> %s' % (DOMAIN_NAME, response.resource_records[0], current_ip))
            else:
                logger.warning('Unknow status for the change: %s' % change)
                logger.debug('%s' % change)

if __name__ == '__main__':
    main()
