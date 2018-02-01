import base64, hashlib
from ctypes import CDLL, POINTER, Structure, create_string_buffer, byref
from ctypes.util import find_library

Security = CDLL(find_library('Security'))
# Importing this via C because haven't figured out how to mix in pyObjc version yet
c_CoreFoundation = CDLL(find_library('CoreFoundation'))

class OpaqueType(Structure):
    pass

OpaqueTypeRef = POINTER(OpaqueType)

CFDataCreate                         = c_CoreFoundation.CFDataCreate
CFDataCreate.restype                 = OpaqueTypeRef
SecCertificateCreateWithData         = Security.SecCertificateCreateWithData
SecCertificateCreateWithData.restype = OpaqueTypeRef

# Convert a C-based CFString back into a python string since we don't have magic
def pystr(cfstringref):
    str_length = c_CoreFoundation.CFStringGetLength(cfstringref) + 1
    str_buff = create_string_buffer(str_length)
    result = c_CoreFoundation.CFStringGetCString(cfstringref, str_buff, str_length, 0)
    return str_buff.value

# Read in a base64 pem file, return raw bytestring
def pem_bytes(cert_path):
    cert_handle = open(cert_path, 'rb')
    cert_data   = cert_handle.read()
    cert_handle.close()
    if not (('-----BEGIN ' in cert_data) and ('-----END ' in cert_data)):
        raise Exception('Error: Certificate does not appear to be .pem file')
    core_data = cert_data.split('-----BEGIN ',1)[-1].replace('\r','\n').split('-----\n',1)[-1].split('\n-----END ',1)[0]
    return base64.b64decode(''.join(core_data.split('\n')))

# Return SHA1 digest for pem certificate at path
def pem_sha1_digest(cert_path):
    raw_bytes = pem_bytes(cert_path)
    return hashlib.sha1(raw_bytes).hexdigest().upper()

# Return CN for pem certifcate at path
def pem_cn(cert_path):
    raw_bytes = pem_bytes(cert_path)
    # Wrap the raw bytes in a CFDataRef
    cfdata_bytes = CFDataCreate(None, raw_bytes, len(raw_bytes))
    # Create a SecCertificateRef from the bytes
    cert_ref = SecCertificateCreateWithData(None, cfdata_bytes)
    # Get the CN from the SecCertificateRef
    cn_ref = OpaqueTypeRef()
    result = Security.SecCertificateCopyCommonName(cert_ref, byref(cn_ref))
    return pystr(cn_ref)
