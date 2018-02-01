#!/usr/bin/env python3

import censys.certificates
import censys.ipv4
from sys import argv

UID = "**CHANGE**"
SECRET = "**CHANGE**"

def is_cloudflare(dn):
    if "cloudflaressl.com" in dn or "cloudflare.com" in dn:
        return True
    return False

def find_certificates(target):
    print("Certificates:")
    certificates = censys.certificates.CensysCertificates(UID, SECRET)
    fingerprints = []
    fields = ["parsed.names", "parsed.extensions.subject_alt_name.dns_names",
              "parsed.fingerprint_sha256", "parsed.subject_dn"]

    for cert in certificates.search("%s and tags: trusted" % target, fields=fields):
        if not is_cloudflare(cert["parsed.subject_dn"]) and target in cert["parsed.names"]:
            fingerprints.append(cert["parsed.fingerprint_sha256"])
            print("\tHost: %s\n\tFingerprint: %s" % (' '.join(cert["parsed.names"]), cert["parsed.fingerprint_sha256"]))
    return fingerprints

def find_hosts(target):
    print("Hosts: %s" % target)
    hosts = censys.ipv4.CensysIPv4(UID, SECRET)

    fields = ["ip"]

    for host in hosts.search(target):
        print("\tFound host: %s" % (host["ip"]))

def main():
    if len(argv) != 2:
        print("Usage: %s <host>" % argv[0])
    else:
        target = argv[1]

    fingerprints = find_certificates(target)
    for fp in fingerprints:
        find_hosts(fp)

if __name__=="__main__":
    main()