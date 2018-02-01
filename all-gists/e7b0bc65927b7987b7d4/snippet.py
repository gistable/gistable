from OpenSSL.crypto import load_certificate, FILETYPE_PEM

cert_file_string = open("esx.crt", "rb").read()
cert = load_certificate(FILETYPE_PEM, cert_file_string)

sha1_fingerprint = cert.digest("sha1")
print sha1_fingerprint