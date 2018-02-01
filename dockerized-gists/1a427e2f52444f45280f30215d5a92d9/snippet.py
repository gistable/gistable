#!/usr/bin/env python
import argparse
import base64
import json
import os


def main():
    parser = argparse.ArgumentParser(
        description="Dump all certificates out of Traefik's acme.json file")
    parser.add_argument('acme_json', help='path to the acme.json file')
    parser.add_argument('dest_dir',
                        help='path to the directory to store the certificate')

    args = parser.parse_args()

    certs = read_certs(args.acme_json)

    print('Found certs for %d domains' % (len(certs),))
    for domain, cert in certs.items():
        print('Writing cert for domain %s' % (domain,))
        write_cert(args.dest_dir, domain, cert)

    print('Done')


def read_cert(storage_dir, filename):
    cert_path = os.path.join(storage_dir, filename)
    if os.path.exists(cert_path):
        with open(cert_path) as cert_file:
            return cert_file.read()
    return None


def write_cert(storage_dir, domain, cert_content):
    cert_path = os.path.join(storage_dir, '%s.pem' % (domain,))
    with open(cert_path, 'wb') as cert_file:
        cert_file.write(cert_content)
    os.chmod(cert_path, 0o600)


def read_certs(acme_json_path):
    with open(acme_json_path) as acme_json_file:
        acme_json = json.load(acme_json_file)

    certs_json = acme_json['DomainsCertificate']['Certs']
    certs = {}
    for cert in certs_json:
        domain = cert['Domains']['Main']
        domain_cert = cert['Certificate']
        # Only get the first cert (should be the most recent)
        if domain not in certs:
            certs[domain] = to_pem_data(domain_cert)

    return certs


def to_pem_data(json_cert):
    return b''.join((base64.b64decode(json_cert['Certificate']),
                     base64.b64decode(json_cert['PrivateKey'])))


if __name__ == '__main__':
    main()
