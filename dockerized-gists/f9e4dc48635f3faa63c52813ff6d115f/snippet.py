#!/usr/bin/env python
import argparse
import base64
import json
import os
import shlex
import subprocess
import sys


def main(raw_args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Grab a certificate out of Traefik's acme.json file")
    parser.add_argument('acme_json', help='path to the acme.json file')
    parser.add_argument('domain', help='domain to get certificate for')
    parser.add_argument('dest_dir',
                        help='path to the directory to store the certificate')
    parser.add_argument(
        '--post-update', required=False,
        help='command to run after updating the certificate')

    args = parser.parse_args(raw_args)

    new_privkey, new_fullchain = read_domain_certs(args.acme_json, args.domain)

    old_privkey = read_cert(args.dest_dir, 'privkey.pem')
    old_fullchain = read_cert(args.dest_dir, 'fullchain.pem')

    if new_privkey != old_privkey or new_fullchain != old_fullchain:
        print('Certificates changed! Writing new files...')
        write_cert(args.dest_dir, 'privkey.pem', new_privkey)
        write_cert(args.dest_dir, 'fullchain.pem', new_fullchain)

        if args.post_update is not None:
            print('Running post update command "%s"' % (args.post_update,))
            post_update(args.post_update)
    else:
        print('Certificates unchanged. Skipping...')

    print('Done')


def read_cert(storage_dir, filename):
    cert_path = os.path.join(storage_dir, filename)
    if os.path.exists(cert_path):
        with open(cert_path) as cert_file:
            return cert_file.read()
    return None


def write_cert(storage_dir, filename, cert_content):
    cert_path = os.path.join(storage_dir, filename)
    with open(cert_path, 'w') as cert_file:
        cert_file.write(cert_content)
    os.chmod(cert_path, 0o600)


def read_domain_certs(acme_json_path, domain):
    with open(acme_json_path) as acme_json_file:
        acme_json = json.load(acme_json_file)

    certs_json = acme_json['DomainsCertificate']['Certs']
    domain_certs = [cert['Certificate'] for cert in certs_json
                    if cert['Domains']['Main'] == domain]

    if not domain_certs:
        raise RuntimeError(
            'Unable to find certificate for domain "%s"' % (domain,))
    elif len(domain_certs) > 1:
        raise RuntimeError(
            'More than one (%d) certificates for domain "%s"' % (domain,))

    [domain_cert] = domain_certs
    return (base64.b64decode(domain_cert['PrivateKey']),
            base64.b64decode(domain_cert['Certificate']))


def post_update(command):
    subprocess.check_call(shlex.split(command))


if __name__ == '__main__':
    main()
