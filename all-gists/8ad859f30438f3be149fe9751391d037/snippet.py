# This was all run from user space
# I haven't tested it with root
# ... but it didn't prompt for any permissions under userspace ^_^
# Tested on 10.11.5

import objc
from Foundation import NSBundle
EAP8021X_bundle = NSBundle.bundleWithPath_('/System/Library/PrivateFrameworks/EAP8021X.framework')
Security_bundle = NSBundle.bundleWithIdentifier_('com.apple.security')

kEAPOLClientDomainUser = 1
kEAPOLClientDomainSystem = 3

E_functions = [
               ('EAPOLClientConfigurationCopyProfiles', '@@'),
               ('EAPOLClientConfigurationCopyAllLoginWindowProfiles', '@@'),
               ('EAPOLClientConfigurationCopyAllSystemProfiles', '@@'),
               ('EAPOLClientConfigurationCreate', '@^@'),
               ('EAPOLClientConfigurationGetProfileWithID', '@@@'),
               ('EAPOLClientItemIDCopyIdentity', '@@i'),
               ('EAPOLClientItemIDCreateWithProfile', '@@'),
               ('EAPOLClientProfileGetAuthenticationProperties', '@@'),
               ('EAPOLClientProfileGetUserDefinedName', '@@'),
               ('EAPOLClientProfileGetWLANSSIDAndSecurityType', '@@o^@'),
               ('EAPOLClientProfileGetID', '@@'),
               ('EAPOLControlCopyStateAndStatus', 'i*o^io^@'),
               ('EAPSecCertificateCopyAttributesDictionary', '@@'),
               ('EAPSecCertificateCopyUserNameString', '@@'),
              ]

S_functions = [
               ('SecIdentityCopyCertificate', 'i@o^@'),
               ('SecCertificateCopyValues', '@@^@o^@'),
               ('SecCertificateCopyData', '@@'),
              ]

objc.loadBundleFunctions(EAP8021X_bundle, globals(), E_functions)
objc.loadBundleFunctions(Security_bundle, globals(), S_functions)

# eap_config contains details about the current EAP session
result, status, eap_config = EAPOLControlCopyStateAndStatus('en0', None, None)
cfg = EAPOLClientConfigurationCreate(None)
# The UniqueIdentifier can be used to look up the 802.1x configuration in use
client_profile = EAPOLClientConfigurationGetProfileWithID(cfg, eap_config['UniqueIdentifier'])
# auth_dict contains the certs and security configuration
auth_dict      = EAPOLClientProfileGetAuthenticationProperties(client_profile)
# display_name is the informal name for the config
display_name = EAPOLClientProfileGetUserDefinedName(client_profile)
# ssid and security_type for the config
ssid_cfdata, security_type = EAPOLClientProfileGetWLANSSIDAndSecurityType(client_profile, None)
ssid = str(ssid_cfdata)
# Find out the associated identity
client_id    = EAPOLClientItemIDCreateWithProfile(client_profile)
identity     = EAPOLClientItemIDCopyIdentity(client_id, kEAPOLClientDomainSystem)
result, cert = SecIdentityCopyCertificate(identity, None)
# This dict contains very basic information like CommonName for the identity's cert
id_dict      = EAPSecCertificateCopyAttributesDictionary(cert)
# username   = EAPSecCertificateCopyUserNameString(cert)

# !!! all OID / x509v3 details about the user cert in a dict
cert_details, errors = SecCertificateCopyValues(cert, None, None)

# Public cert used by identity
cert_bytes = SecCertificateCopyData(cert)
# You can write str(cert_bytes) back out to a file and it'll be the
# DER .cer certificate of the public cert of the 802.1x identity
