import objc
from ctypes import c_char
from Foundation import NSBundle
Security = NSBundle.bundleWithIdentifier_('com.apple.security')

S_functions = [
               ('SecKeychainGetTypeID', 'I'),
               ('SecKeychainItemGetTypeID', 'I'),
               ('SecKeychainAddGenericPassword', 'i^{OpaqueSecKeychainRef=}I*I*I*o^^{OpaqueSecKeychainItemRef}'),
               ('SecKeychainOpen', 'i*o^^{OpaqueSecKeychainRef}'),
               ('SecKeychainFindGenericPassword', 'i@I*I*o^Io^^{OpaquePassBuff}o^^{OpaqueSecKeychainItemRef}'),
              ]

objc.loadBundleFunctions(Security, globals(), S_functions)

SecKeychainRef     = objc.registerCFSignature('SecKeychainRef',     '^{OpaqueSecKeychainRef=}',     SecKeychainGetTypeID())
SecKeychainItemRef = objc.registerCFSignature('SecKeychainItemRef', '^{OpaqueSecKeychainItemRef=}', SecKeychainItemGetTypeID())
PassBuffRef = objc.createOpaquePointerType("PassBuffRef", b"^{OpaquePassBuff=}", None)

def resolve_password(password_length, password_buffer):
    return (c_char*password_length).from_address(password_buffer.__pointer__)[:].decode('utf-8')

# Get the login keychain
result, login_keychain = SecKeychainOpen('login.keychain', None)

# Password details - service is the display name, acccount is the account name/user name
svc_n = "test-service"
act_n = "test-account"

# Store a password
act_p = "test-pass"
result, keychain_item = SecKeychainAddGenericPassword(login_keychain, len(svc_n), svc_n, len(act_n), act_n, len(act_p), act_p, None)

# Retrieve a password
result, password_length, password_buffer, keychain_item = SecKeychainFindGenericPassword(login_keychain, len(svc_n), svc_n, len(act_n), act_n, None, None, None)
password = None
if (result == 0) and (password_length != 0):
    # We apparently were able to find a password
    password = resolve_password(password_length, password_buffer)
