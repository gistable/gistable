# To run, provide the path to a signed profile at the command line:
# ./unsignprofile.py SignedProfile.mobileconfig

from M2Crypto import SMIME, X509, m2, BIO
from plistlib import *
import sys
import logging

# Can be any file probably since we're not verifying.
certstore_path = "/etc/ssl/certs/ca-certificates.crt"
file_descriptor = open(sys.argv[1], 'rb')
input_bio = BIO.File(file_descriptor)
signer = SMIME.SMIME()
cert_store = X509.X509_Store()
cert_store.load_info(certstore_path)
signer.set_x509_store(cert_store)
try: 
    p7 = SMIME.PKCS7(m2.pkcs7_read_bio_der(input_bio._ptr()), 1)
except SMIME.SMIME_Error, e:
    logging.error('load pkcs7 error: ' + str(e))
sk3 = p7.get0_signers(X509.X509_Stack())
signer.set_x509_stack(sk3)
data_bio = None

content = signer.verify(p7, data_bio, flags=SMIME.PKCS7_NOVERIFY)

# Printing the contents of the profile/plist, modify to save to file with write()
print readPlistFromString(content)