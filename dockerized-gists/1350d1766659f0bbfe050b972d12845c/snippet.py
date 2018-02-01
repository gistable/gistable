#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError
from socket import getfqdn
import hvac
import sys
import os
import os.path

class PositiveIntegerValidator:
    def validate(self, document):
        value = document.text
        if not value:
            raise ValidationError(message='Must be a numeric value')
        if not value.isdigit():
            raise ValidationError(message='Must be a numeric value')
        if int(value) < 1:
            raise ValidationError(message='Must be greater than 1')


class StringValidator:
    def validate(self, document):
        if not document.text:
            raise ValidationError(message='Must not be empty')


def vault_client():
    return hvac.Client(url=vault_addr(), token=vault_token())


def vault_addr():
    return os.environ.get('VAULT_ADDR', 'http://127.0.0.1:8200')


def vault_token():
    if 'VAULT_TOKEN' in os.environ:
        return os.environ['VAULT_TOKEN']
    try:
        return open(os.path.expanduser('~/.vault-token')).read().rstrip()
    except IOError:
        raise RuntimeError('A vault token was not found in ~/.vault-token '
                           'or in the VAULT_TOKEN environment variable.')


def prompt_for_secret_shares():
    print("Enter the number of secret shares to create. This is the number of\n"
          "key fragments that will be created that you can distribute among\n"
          "the team.\n")
    num = prompt('Number of secret shares: ', default='5',
            validator=PositiveIntegerValidator())
    print()
    return int(num)


def prompt_for_secret_threshold():
    print("\nEnter the number secret shares that must be entered to unseal the\n"
          "vault.  This should be 2 or more.\n")
    num = prompt('Unseal threshold: ', default='3',
            validator=PositiveIntegerValidator())
    print()
    return int(num)


def initialize_vault(shares, threshold):
    client = vault_client()
    result = client.initialize(shares, threshold)
    return result['root_token'], result['keys']


def unseal_vault(unseal_keys):
    vault_client().unseal_multi(unseal_keys)


def setup_vault_server_ca():
    client = vault_client()
    print("\nThe next step is to set up the TLS certificate and key that\n"
          "protects communications with Vault itself.")
    print("\nEnter a Common Name for the root certificate that will be used to\n"
          "sign this Vault's intermediate certificate.  Usually the\n"
          "name will be like 'Vault XXXX Server Root CA', where 'XXXX' is\n"
          "the scope of the data Vault protects, like 'Production',\n"
          "'Master', etc.\n")
    root_cn = prompt('Name: ', default='Vault Test Server Root CA',
            validator=StringValidator())
    print("\nEnter a Common Name for the intermediate certificate that will be\n"
          "used to sign this Vault's server certificates.  Usually the\n"
          "name will be like 'Vault XXXX Server Intermediate CA', where\n"
          "'XXXX' is the scope of the data Vault protects, like\n"
          "'Production', 'Master', etc.\n")
    intermediate_cn = prompt('Name: ',
            default='Vault Test Server Intermediate CA',
            validator=StringValidator())
    root_mount = 'vault_server_root_ca'
    intermediate_mount = 'vault_server_intermediate_ca'
    intermediate_role = 'server'
    client.enable_secret_backend('pki', mount_point=root_mount,
            config={'max_lease_ttl':'876000h'})
    client.enable_secret_backend('pki', mount_point=intermediate_mount,
            config={'max_lease_ttl':'875999h'})
    response = client.write('{}/root/generate/internal'.format(root_mount),
            common_name=root_cn, ttl='87600h')
    root_cert = response['data']['certificate'] + "\n"
    response = client.write('{}/intermediate/generate/internal'.format(intermediate_mount),
            common_name=intermediate_cn)
    intermediate_csr = response['data']['csr']
    response = client.write('{}/root/sign-intermediate'.format(root_mount),
            csr=intermediate_csr, common_name=intermediate_cn, ttl='87599h')
    intermediate_cert = response['data']['certificate'] + "\n"
    response = client.write('{}/intermediate/set-signed'.format(intermediate_mount),
            certificate=intermediate_cert)
    return root_cert, intermediate_cert, intermediate_mount


def issue_vault_certificate(ca):
    client = vault_client()
    fqdn = getfqdn()
    domains = [fqdn, 'localhost']
    print("\nEnter all hostnames at which this Vault server (or its replica)\n"
          "might be known to clients (for TLS hostname verification\n"
          "purposes).  Include any Consul DNS names too (e.g.\n"
          "'vault.service.consul').\n\n"
          "For convenience, the names '{}', 'localhost' and '127.0.0.1'\n"
          "will be automatically added to the certificate.\n".format(fqdn))
    while True:
        domain = prompt('Hostname: ')
        if domain:
            if domain not in domains:
                domains.append(domain)
        else:
            if len(domains) > 0:
                break
    client.write('{}/roles/servers'.format(ca),
            enforce_hostnames=False,
            allow_localhost=True,
            allow_bare_domains=True,
            allowed_domains=','.join(['Vault Server'] + domains),
            allow_subdomains=False)
    response = client.write('{}/issue/servers'.format(ca),
            common_name='Vault Server',
            ttl='43830h', alt_names=','.join(domains),
            ip_sans='127.0.0.1')
    return response['data']['certificate'] + "\n", response['data']['private_key'] + "\n"


def enable_auditing():
    client = vault_client()
    client.enable_audit_backend('file', options={'file_path':'/dev/stdout'})


def main():
    shares = prompt_for_secret_shares()
    threshold = prompt_for_secret_threshold()
    root_token, unseal_keys = initialize_vault(shares, threshold)
    f = os.open(os.path.expanduser('~/.vault-token'), os.O_WRONLY | os.O_CREAT, 0600)
    os.write(f, root_token)
    os.close(f)
    unseal_vault(unseal_keys)
    enable_auditing()
    root_cert, intermediate_cert, intermediate_mount = setup_vault_server_ca()
    vault_cert, vault_key = issue_vault_certificate(intermediate_mount)
    ca_file = 'vault_ca.pem'
    cert_file = 'vault.pem'
    key_file = 'vault.key'
    with open(ca_file, 'w') as f:
        f.write(root_cert)
    with open(cert_file, 'w') as f:
        f.write(vault_cert + intermediate_cert + root_cert)
    f = os.open(key_file, os.O_WRONLY | os.O_CREAT, 0600)
    os.write(f, vault_key)
    os.close(f)
    print("\nRoot token: " + root_token)
    print("\nUnseal keys (1 per line):")
    for key in unseal_keys:
        print(key)
    print("\nThe Vault CA file is located in {}".format(ca_file))
    print("Distribute it to Vault clients and put it in their trust stores\n"
          "so that they don't receive validation errors when connecting to\n"
          "this Vault cluster.  That includes the Vault server itself, so\n"
          "health checks can be performed by Consul, etc.")
    print("\nThe Vault key file is located in {}".format(key_file))
    print("Copy it to /etc/pki/tls/private/vault.key.  Make sure the file\n"
          "is mode 0600 and owned by the 'vault' user.")
    print("\nThe Vault certificate file is located in {}".format(cert_file))
    print("Copy it to /etc/pki/tls/certs/vault.pem.  Make sure the file\n"
          "is mode 0644.")
    print("\nAfter this has completed, restart Vault so it uses the new\n"
          "certificate and key.")
    print("\n(The same key and certificate should be used for the Vault\n"
          "replica in this datacenter.)")
    sys.exit(0)


if __name__ == '__main__':
    main()