import logging

import zerigodns 
import boto
from boto.route53.record import ResourceRecordSets
from boto.s3.website import RedirectLocation

# There is no API for these so we have to embed and lookup
# https://forums.aws.amazon.com/thread.jspa?threadID=116724
# http://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region
ENDPOINT_HOSTED_ZONE_IDS = {
    "s3-website-us-east-1.amazonaws.com":"Z3AQBSTGFYJSTF",
    "s3-website-us-west-2.amazonaws.com":"Z3BJ6K6RIION7M",  
    "s3-website-us-west-1.amazonaws.com":"Z2F56UZL2M1ACD",
    "s3-website-eu-west-1.amazonaws.com":"Z1BKCTXD74EZPE",
    "s3-website-ap-southeast-1.amazonaws.com":"Z3O0J2DXBE1FTB",
    "s3-website-ap-southeast-2.amazonaws.com":"Z1WCIGYICN2BYD",
    "s3-website-ap-northeast-1.amazonaws.com":"Z2M4EHUR26P7ZW",
    "s3-website-sa-east-1.amazonaws.com":"Z7KQH4QJS55SO",   
    "s3-website-us-gov-west-1.amazonaws.com":"Z31GFT0UA1I2HV"   
}

def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

def migrate_zerigo_to_route53(
    domain_name,
    zerigo_api_user,
    zerigo_api_key,
    aws_access_key_id,
    aws_secret_access_key,
    comment='migrated from zerigo',
    use_s3_for_redirects=True,
    dry_run=False):

    # ZERIGO
    zerigo = zerigodns.NSZone(zerigo_api_user, zerigo_api_key)

    try:
        zone = zerigo.find_by_domain(domain_name)
    except zerigodns.ZerigoNotFound as ex:
        logging.exception(ex)
        logging.error('Domain not found in zerigo')
        return

    hosts = zone.hosts
    record_data = dict()
    for host in hosts:
        key = (host.hostname, host.host_type)
        if not record_data.has_key(key):
            record_data[key] = dict(
                name=host.hostname and (host.hostname + '.' + domain_name) or domain_name, 
                type=host.host_type, 
                ttl=host.ttl or 3600,
                values=[])
        value = host.data
        if host.host_type == 'MX':
            value = (str(host.priority or 1) + ' ' + host.data)
        record_data[key]['values'].append(value)

    # ROUTE 53
    route53 = boto.connect_route53(aws_access_key_id, aws_secret_access_key)
    hosted_zone_id = None

    if not dry_run:

        hosted_zone = route53.get_hosted_zone_by_name(domain_name)

        if hosted_zone:
            hosted_zone_id = hosted_zone['GetHostedZoneResponse']['HostedZone']['Id'].split("/")[2]

        if hosted_zone is None:
            hosted_zone = route53.create_hosted_zone(
                domain_name=domain_name, 
                comment=comment)
            hosted_zone_id = hosted_zone['CreateHostedZoneResponse']['HostedZone']['Id'].split("/")[2]
    
    

    s3 = None # used for creating buckets for redirects

    for chunk in chunks(record_data.values(), 50): # errors if we do > 100 at a time

        record_set = ResourceRecordSets(
            connection=route53,
            hosted_zone_id=hosted_zone_id,
            comment=comment)

        for record in chunk:

            record_type = record['type']

            # route53 doesnt support URL redirect record type, so we have to use S3 and alias 
            # https://devcenter.heroku.com/articles/route-53#naked-root-domain
            if record_type == 'URL' and use_s3_for_redirects:
                if s3 is None: 
                    s3 = boto.connect_s3(aws_access_key_id, aws_secret_access_key)
                bucket_name = record['name']
                if not dry_run: 
                    bucket = s3.lookup(bucket_name) or s3.create_bucket(bucket_name)
                    redirect_to = record['values'][0].split("://")[1] # cant have http:// prefix http only
                    logging.debug('redirect to: '+ redirect_to)
                    bucket.configure_website(redirect_all_requests_to=RedirectLocation(redirect_to))
                    website_endpoint = bucket.get_website_endpoint()
                    endpoint = website_endpoint.split(record['name']+".")[1]
                    record_set.add_change(
                        'CREATE',
                        name=record['name'],
                        type='A',
                        ttl=record['ttl'],
                        alias_hosted_zone_id=ENDPOINT_HOSTED_ZONE_IDS[endpoint],
                        alias_dns_name=endpoint)

            elif record_type in ('CNAME', 'A', 'MX', 'TXT'):

                logging.debug("adding record: %r" % record)

                if not dry_run:
                    values = record.pop('values')
                    change = record_set.add_change('CREATE', **record)
                    for value in values:
                        if record_type == 'TXT':
                            value = '"'+value+'"'
                        change.add_value(value) 
            else:
                logging.info("Unsupported record type: %s" % record_type)

        if not dry_run:
            record_set.commit()

if __name__ == '__main__':
    
    import os, sys, argparse

    parser = argparse.ArgumentParser(description='Migrates zone for zerigo to route53')

    parser.add_argument('--access_key_id', '-a', help='Your AWS Access Key ID. Could also be set using the "EC2_ACCESS_KEY_ID" environment variable')
    parser.add_argument('--secret_access_key', '-s', help='Your AWS Secret Access Key. Could also be set using the "EC2_SECRET_ACCESS_KEY" environment variable')
    
    parser.add_argument('--api-user', '-u', help='Zerigo API user. Could also be set using "ZERIGO_API_USER" environment variable')
    parser.add_argument('--api-key', '-k', help='Zerigo API key. Could also be set using "ZERIGO_API_KEY" environment variable')

    parser.add_argument('--comment', '-c', default='migrated from zerigo', help='Comment to add to zone')
    parser.add_argument('--dry-run', '-n', action='store_true', default=False, help='Don\'t actually make change, do everything else')
    parser.add_argument('--redirects', '-r', action='store_false', default=True, help='Use s3 for redirects')
    parser.add_argument('--debug', '-d', action='store_true', default=False, help='Turn debugging on')

    parser.add_argument('domain_name')

    args = parser.parse_args()

    if not args.access_key_id:
        args.access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    if not args.secret_access_key:
        args.secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

    if not args.api_user:
        args.api_user = os.environ.get('ZERIGO_API_USER')
    if not args.api_key:
        args.api_key = os.environ.get('ZERIGO_API_KEY')

    if not args.access_key_id or not args.secret_access_key or not args.api_user or not args.api_key:
        print 'ERROR: Missing AWS or Zerigo credentials. See help...\n'
        parser.print_help()
        sys.exit(2)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    migrate_zerigo_to_route53(
        args.domain_name,
        args.api_user,
        args.api_key,
        args.access_key_id,
        args.secret_access_key,
        args.comment,
        args.redirects,
        args.dry_run)




