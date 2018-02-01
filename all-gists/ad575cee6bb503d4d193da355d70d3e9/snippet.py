import ssl, base64, objc
from Foundation import NSBundle
Security = NSBundle.bundleWithIdentifier_('com.apple.security')

S_functions = [
               ('SecCertificateCreateWithData', '@@@'),
               ('SecCertificateCopyValues', '@@^@o^@'),
              ]

objc.loadBundleFunctions(Security, globals(), S_functions)

server_pem    = ssl.get_server_certificate(('www.google.com', 443))
pem_lines     = server_pem.splitlines()
pem_base64    = ''.join([x for x in pem_lines if 'CERTIFICATE---' not in x])
server_der    = base64.b64decode(pem_base64)
server_cert   = SecCertificateCreateWithData(None, buffer(server_der))

cert_details, errors = SecCertificateCopyValues(server_cert, None, None)