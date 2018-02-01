#!/usr/bin/env python

from M2Crypto import SMIME, X509, BIO, m2
import plistlib
import sys

if len(sys.argv) < 3:
  print "Usage: %s [Provisioning Profile] [Out .xcconfig]" % __file__
	exit()

inProfile = sys.argv[1]
outXcConfig = sys.argv[2]

provision = open(inProfile, 'r')

inBio = BIO.File(provision)
pkcs7 = SMIME.PKCS7(m2.pkcs7_read_bio_der(inBio._ptr()))

smime = SMIME.SMIME()
stack = X509.X509_Stack()
smime.set_x509_stack(stack)

store = X509.X509_Store()
smime.set_x509_store(store)

dataBio = None
blob = smime.verify(pkcs7, dataBio, SMIME.PKCS7_NOVERIFY | SMIME.PKCS7_NOSIGS)

certs = pkcs7.get0_signers(stack)
signer = certs[0]

items = signer.get_subject().get_entries_by_nid(X509.X509_Name.nid["CN"])

plist = plistlib.readPlistFromString(blob)

developerPEM = "-----BEGIN CERTIFICATE-----\n%s-----END CERTIFICATE-----" % plist["DeveloperCertificates"][0].asBase64()
developerCert = X509.load_cert_string(developerPEM)
items = developerCert.get_subject().get_entries_by_nid(X509.X509_Name.nid["CN"])

if len(items) > 0:
	codeSignIdentity = items[0].get_data()
	open(outXcConfig, 'w').write("CODE_SIGN_IDENTITY = %s\nPROVISIONING_PROFILE = %s\n" % (codeSignIdentity, plist["UUID"]))



