import argparse
import boto
import boto.ec2.elb
import time

AWS_ACCOUNT_ID = '0123456789'
REGIONS = ['us-west-2', 'us-east-1', 'eu-west-1']

def get_matching_elbs(region, ssl_cert_arn):
    print "getting matching elbs in region {}".format(region)
    conn = boto.ec2.elb.connect_to_region(region)
    elbs = conn.get_all_load_balancers()
    _matches = []
    for elb in elbs:
        for listener in elb.listeners:
            if listener.ssl_certificate_id == ssl_cert_arn:
                # appends a tuple of (elb boto object, matching port)
                _matches.append((elb, listener.load_balancer_port))
                print "matched: {} / port {} / cert {}".format(elb.name, listener.load_balancer_port, ssl_cert_arn)
    return _matches

def update_certificate(cert_name, cert_path, privkey_path, chain_path=None):
    cert_body = cert_path.read()
    private_key = privkey_path.read()
    if chain_path:
        cert_chain = chain_path.read()
    else:
        cert_chain = None
    conn = boto.connect_iam()
    try:
        conn.delete_server_cert(cert_name)
        print "removed old cert: {}".format(cert_name)
    except Exception as e:
        print "error removing old cert {}".format(str(e))
    try:
        conn.upload_server_cert(cert_name,
                                cert_body=cert_body,
                                private_key=private_key,
                                cert_chain=cert_chain)
        print "updated certificate {}".format(cert_name)
    except Exception as e:
        print "error uploading new cert {}".format(str(e))
    conn.close()

def update_elb_cert(elb, ssl_cert_arn):
    _elb = elb[0]
    _port = elb[1]
    success = False
    tries = 1
    while not success and tries <= 5:
        try:
            _elb.set_listener_SSL_certificate(_port, ssl_cert_arn)
            success = True
        except Exception as e:
            tries += 1
            print "try {}: failed to update elb {}, {}".format(tries, _elb.name, str(e))
            time.sleep(1)
    if success:
        print "updated {} / port {} with new cert {}".format(_elb.name, _port, ssl_cert_arn)
    else:
        print "totally failed: {} / port {} with new cert {}".format(_elb.name, _port, ssl_cert_arn)


def main():
    parser = argparse.ArgumentParser('certificate updater')
    parser.add_argument('--name', help='cert AWS ARN', required=True)
    parser.add_argument('--cert', help="path to new PEM-foramtted cert file", required=True, type=file)
    parser.add_argument('--private_key', help="path to new PEM-foramtted private key file", required=True, type=file)
    parser.add_argument('--cert_chain', help="path to new PEM-formatted cert chain file", type=file)
    args = parser.parse_args()

    cert_arn = 'arn:aws:iam::' + AWS_ACCOUNT_ID + ':server-certificate/' + args.name

    # get all ELBs that use the old cert
    elbs = []
    for r in REGIONS:
        elbs.extend(get_matching_elbs(r, cert_arn))

    # update the cert 
    update_certificate(args.name, args.cert, args.private_key, args.cert_chain)

    # let EC2 catch up with IAM
    time.sleep(10)

    # update all ELBs with new cert
    for elb in elbs:
        update_elb_cert(elb, cert_arn)
        time.sleep(1)

    print "finished"

if __name__ == "__main__":
    main()
