import os.path, base64
from ctypes import CDLL, Structure, POINTER, byref, addressof, create_string_buffer, c_int, c_uint, c_ubyte, c_void_p, c_size_t
from CoreFoundation import kCFStringEncodingUTF8

# Wheee!
Security    = CDLL('/System/Library/Frameworks/Security.Framework/Versions/Current/Security')
# I don't use the pyObjC CoreFoundation import because it attempts to bridge between CF, NS, and python.
# When you try to mix it with Security.Foundation (pure C / CF), you get nasty results.
# So I directly import CoreFoundation to work with CFTypes to keep it pure of NS/python bridges.
CFoundation = CDLL('/System/Library/Frameworks/CoreFoundation.Framework/Versions/Current/CoreFoundation')

class OpaqueType(Structure):
    pass

# Combined with the above, this is essentially an opaque wrapper around pointers to various
# data types. Just enough syntactic sugar to keep python from bugging out with raw C pointers.
OpaqueTypeRef = POINTER(OpaqueType)

# Per <sys/param.h> and <sys/syslimits.h>
MAXPATHLEN = 1024

# Setting the return type to one of our opaque pointer wrappers so python doesn't bug out.
CFArrayCreate                     = CFoundation.CFArrayCreate
CFArrayCreate.restype             = OpaqueTypeRef
CFArrayCreateMutable              = CFoundation.CFArrayCreateMutable
CFArrayCreateMutable.restype      = OpaqueTypeRef
CFArrayGetValueAtIndex            = CFoundation.CFArrayGetValueAtIndex
CFArrayGetValueAtIndex.restype    = OpaqueTypeRef
CFDataCreate                      = CFoundation.CFDataCreate
CFDataCreate.restype              = OpaqueTypeRef
CFStringCreateWithCString         = CFoundation.CFStringCreateWithCString
CFStringCreateWithCString.restype = OpaqueTypeRef

CSSM_CERT_X_509v3 = 3
CSSM_CERT_ENCODING_DER = 3

kSecFormatUnknown = 0
kSecItemTypeUnknown = 0
kSecKeySecurePassphrase = 2

kSecTrustSettingsDomainUser = 0

# Per SecKeychain.h
kSecPreferencesDomainUser      = 0
kSecPreferencesDomainSystem    = 1
# kSecPreferencesDomainCommon    = 2
# Interestingly, https://developer.apple.com/library/mac/documentation/security/Reference/keychainservices/Reference/reference.html
# also includes kSecPreferencesDomainAlternate and kSecPreferencesDomainDynamic.
# However, kSecPreferencesDomainAlternate is not listed in SecKeychain.h, which means the header file disagrees with the
# documentation on the enumeration value for the domains. In testing with SecKeychainCopyDomainSearchList, it doesn't recognize a
# value beyond 3 - so that would seem to indicate the public documentation is wrong. Doesn't really matter since we don't
# care about these two anyways - just something odd to note.

class SecKeychainSettings(Structure):
    pass

SecKeychainSettings._fields_ = [
    ('version', c_uint),
    ('lockOnSleep', c_ubyte),
    ('useLockInterval', c_ubyte),
    ('lockInterval', c_uint),
]

class SecKeyImportExportParameters(Structure):
    pass

SecKeyImportExportParameters._fields_ = [
    ('version', c_uint),
    ('flags', c_uint),
    ('passphrase', OpaqueTypeRef),
    ('alertTitle', OpaqueTypeRef),
    ('alertPrompt', OpaqueTypeRef),
    ('accessRef', OpaqueTypeRef),
    ('keyUsage', c_uint),
    ('keyAttributes', c_uint),
]

class CSSM_DATA(Structure):
    pass

CSSM_DATA._fields_ = [
    ('Length', c_size_t),
    ('Data', c_void_p),
]

def safe_release(cf_ref):
    if cf_ref:
        CFoundation.CFRelease(cf_ref)

def get_keychain_path(a_keychain):
    path_length = c_int(MAXPATHLEN)
    path_name   = create_string_buffer('\0'*(MAXPATHLEN+1), MAXPATHLEN+1)
    result      = Security.SecKeychainGetPath(a_keychain, byref(path_length), path_name)
    # We don't even need the path_length because path_name was made with the create_string_buffer
    # helper, which has nice python bindings around C strings / auto detection for null termination
    return path_name.value

def resolve_keychain_name(keychain_name):
    # Basically you open a reference and then resolve the path OS X is looking for it at
    keychainRef = OpaqueTypeRef()
    result = Security.SecKeychainOpen(keychain_name, byref(keychainRef))
    if not keychainRef:
        # Weird, it couldn't resolve - this shouldn't happen
        return None
    # Get the path
    keychain_path = get_keychain_path(keychainRef)
    # Release the ref
    safe_release(keychainRef)
    return keychain_path

def list_our_keychains(kDomain=None):
    if not kDomain:
        # Default to user domain
        kDomain = kSecPreferencesDomainUser
    keychain_paths = []
    search_list = OpaqueTypeRef()
    # Look up our list of keychain paths in the user domain, pass the results back in search_list
    result = Security.SecKeychainCopyDomainSearchList(kDomain, byref(search_list))
    # Return code is zero on success
    if (result != 0):
        raise Exception('Error: Could not get keychain search list for some reason')
    # SecKeychainCopyDomainSearchList is pretty gross. It can return a single SecKeychainRef
    # ... OR it can return a CFArray of them. So you have to check what you're getting.
    if (CFoundation.CFGetTypeID(search_list) == Security.SecKeychainGetTypeID()):
        # It's a SecKeychain, just get the path value directly
        keychain_paths.append(get_keychain_path(search_list))
    elif (CFoundation.CFGetTypeID(search_list) == CFoundation.CFArrayGetTypeID()):
        # It's a CFArray of SecKeychains, gotta loop
        count = CFoundation.CFArrayGetCount(search_list)
        for i in range(count):
            # Work with the items one at a time
            a_keychain = CFArrayGetValueAtIndex(search_list, i)
            keychain_paths.append(get_keychain_path(a_keychain))
    return keychain_paths

# >>> list_our_keychains(kSecPreferencesDomainUser)
# ['/Users/mike/Library/Keychains/login.keychain']

# >>> list_our_keychains(kSecPreferencesDomainSystem)
# ['/Library/Keychains/System.keychain']

def keychain_present_in_search(keychain_name):
    # In the user domain
    return resolve_keychain_name(keychain_name) in list_our_keychains(kSecPreferencesDomainUser)

def set_keychain_search(keychain_list):
    # In the user domain
    # Note: SecKeychainOpen, by design, does not fail for keychain paths that don't exist.
    # Keychains can be kept on smartcard devices that fall under the 'dynamic' domain
    # in that they should be part of the search path, but aren't guaranteed to always be there.
    # See: http://lists.apple.com/archives/apple-cdsa/2006/Feb/msg00063.html
    # Also: Non-absolute paths are considered to be located (by SecKeychainOpen) in the
    # ~/Library/Keychains path. This isn't really well documented by Apple.
    problem = False
    if not keychain_list:
        # Need to create a blank list and set our search path to it.
        search_arrayRef = CFArrayCreate(None, None, 0, CFoundation.kCFTypeArrayCallBacks)
    else:
        # One or more items. Need to create an array of them
        search_arrayRef  = CFArrayCreateMutable(None, 0, CFoundation.kCFTypeArrayCallBacks)
        for keychain_path in keychain_list:
            # Set up a null pointer to store the ref at
            keychainRef = OpaqueTypeRef()
            result = Security.SecKeychainOpen(keychain_path, byref(keychainRef))
            if (result != 0) or (not keychainRef):
                # There was a problem, don't set any paths
                problem = True
            else:
                # Append the keychain reference and release it
                result = CFoundation.CFArrayAppendValue(search_arrayRef, keychainRef)
                safe_release(keychainRef)
    # Attempt to set the search paths
    result = Security.SecKeychainSetDomainSearchList(kSecPreferencesDomainUser, search_arrayRef)
    safe_release(search_arrayRef)
    if (result != 0) or (problem):
        raise Exception('Could not set the search path.', result)

def add_keychain_search(keychain_name):
    # In the user domain
    if keychain_present_in_search(keychain_name):
        # It's already there, just return
        return
    # Otherwise, need to add it to the search path - it'll go at the end
    new_path_list = list_our_keychains()
    # Remove it from the list
    new_path_list.append(keychain_name)
    # Set our search path to the new list
    set_keychain_search(new_path_list)

def remove_keychain_search(keychain_name):
    # In the user domain, some safety to keep from removing a login keychain
    if not keychain_present_in_search(keychain_name):
        # It's not in the search path currently, so just return
        return
    full_name = resolve_keychain_name(keychain_name)
    if (full_name == resolve_keychain_name('login.keychain')):
        # Safety feature - don't want to remove the login keychain accidentally
        return
    # Otherwise, it is in the search path - need to remove it
    new_path_list = list_our_keychains()
    # Remove it from the list
    new_path_list.remove(full_name)
    # Set our search path to the new list
    set_keychain_search(new_path_list)

def check_keychain_status(keychain_name):
    # In the user domain
    # This is a higher level function the others rely on
    # It checks availability of the keychain and, if available, current state
    # Return value is a boolean tuple: (usable, unlocked, readable, writable)
    status = [False, None, None, None]
    # Get a keychain reference
    keychainRef = OpaqueTypeRef()
    result = Security.SecKeychainOpen(keychain_name, byref(keychainRef))
    if not keychainRef:
        # Weird, it couldn't resolve - this shouldn't happen
        return status
    # Check on the status of the keychain
    status_mask = c_uint(0)
    result = Security.SecKeychainGetStatus(keychainRef, byref(status_mask))
    if result == 0:
        # Keychain is available and usable - now to unpack status_mask
        # Quick hack:
        # 1 = unlocked
        # 2 = readable
        # 4 = writable
        # Format the integer into a 3 digit binary string ('000','001', etc), map True for 1 & False for 0 per digit,
        # then reverse the order (so they're in order: 1, 2, 4)
        status = [True] + map(lambda x: x=='1','{0:03b}'.format(status_mask.value))[::-1]
    safe_release(keychainRef)
    return status

def keychain_available(keychain_name):
    return check_keychain_status(keychain_name)[0]

def keychain_unlocked(keychain_name):
    # Hell, even the security tool won't tell you (directly) if a keychain is unlocked ...
    exists, unlocked, readable, writable = check_keychain_status(keychain_name)
    if not exists:
        raise Exception('Error: No such keychain')
    return unlocked

def lock_keychain(keychain_name):
    exists, unlocked, readable, writable = check_keychain_status(keychain_name)
    if not exists:
        raise Exception('Error: No such keychain')
    if not unlocked:
        # Already locked, no need to lock it again
        return
    # Ok, time to lock it
    keychainRef = OpaqueTypeRef()
    result = Security.SecKeychainOpen(keychain_name, byref(keychainRef))
    if not keychainRef:
        # Weird, it couldn't resolve - this shouldn't happen
        raise Exception("Error: Something odd happened that shouldn't.")
    # Perform lock
    result = Security.SecKeychainLock(keychainRef)
    # Release the reference
    safe_release(keychainRef)
    # Report on the result
    if result != 0:
        raise Exception('Error: Non-zero return on lock ..?', result)

def unlock_keychain(keychain_name, password):
    # This is baby steps here. I'm not supporting, for instance, UTF-8 yet
    exists, unlocked, readable, writable = check_keychain_status(keychain_name)
    if not exists:
        raise Exception('Error: No such keychain')
    if unlocked:
        # Already unlocked, no need to lock it again
        return
    # Ok, time to unlock it
    keychainRef = OpaqueTypeRef()
    result = Security.SecKeychainOpen(keychain_name, byref(keychainRef))
    if not keychainRef:
        # Weird, it couldn't resolve - this shouldn't happen
        raise Exception("Error: Something odd happened that shouldn't.")    
    # Perform unlock
    result = Security.SecKeychainUnlock(keychainRef, len(password), password, True)
    # Release the reference
    safe_release(keychainRef)
    # Report on the result
    if result != 0:
        raise Exception('Error: Non-zero return on unlock ..?', result)

def set_keychain_settings(keychain_name, sleep_lock=False, interval_lock=False, interval_time=2147483647):
    # If you unlock the keychain before changing settings, you do not get prompted via GUI for non-root
    # Setting the interval time to anything other than the default 2147483647 overrides/ignores any value
    # for interval_lock and forces it to True.
    exists, unlocked, readable, writable = check_keychain_status(keychain_name)
    if not exists:
        raise Exception('Error: No such keychain')
    # Make our settings object
    # Version number for settings is supposed to be '1'
    settings_struct = SecKeychainSettings(1, sleep_lock, interval_lock, interval_time)
    if settings_struct.lockInterval != 2147483647:
        interval_lock = True
    # Time to change settings
    keychainRef = OpaqueTypeRef()
    result = Security.SecKeychainOpen(keychain_name, byref(keychainRef))
    if not keychainRef:
        # Weird, it couldn't resolve - this shouldn't happen
        raise Exception("Error: Something odd happened that shouldn't.")
    # Perform settings change
    result = Security.SecKeychainSetSettings(keychainRef, byref(settings_struct))
    # Release the reference
    safe_release(keychainRef)
    if result != 0:
        raise Exception('Error: Something went wrong with that settings change', result)

def get_keychain_settings(keychain_name):
    # If you unlock the keychain before changing settings, you do not get prompted via GUI for non-root
    # Results returned are: bool sleep_lock, bool interval_lock, int interval_time (in seconds)
    exists, unlocked, readable, writable = check_keychain_status(keychain_name)
    if not exists:
        raise Exception('Error: No such keychain')
    # Make our settings object, data to be filled in
    # Version number for settings is supposed to be '1'
    settings_struct = SecKeychainSettings(1, 0, 0, 0)
    # Time to get settings
    keychainRef = OpaqueTypeRef()
    result = Security.SecKeychainOpen(keychain_name, byref(keychainRef))
    if not keychainRef:
        # Weird, it couldn't resolve - this shouldn't happen
        raise Exception("Error: Something odd happened that shouldn't.")
    # Perform settings change
    result = Security.SecKeychainCopySettings(keychainRef, byref(settings_struct))
    # Release the reference
    safe_release(keychainRef)
    if result != 0:
        raise Exception('Error: Something went wrong with that settings change', result)
    # Apparently useLockInterval is always false. Whether it will lock or not is purely based on the timer value.
    return (bool(settings_struct.lockOnSleep), settings_struct.lockInterval!=2147483647, settings_struct.lockInterval)

def create_keychain(keychain_name, password, auto_search=True):
    # The zero is for 'do_prompt' for password
    # The None is for default access rights for the keychain
    if not password:
        raise Exception('Error: Password must be provided')
    if keychain_available(keychain_name):
        raise Exception('Error: Keychain already exists with this name')
    keychainRef = OpaqueTypeRef()
    result = Security.SecKeychainCreate(keychain_name, len(str(password)), str(password), 0, None, byref(keychainRef))
    safe_release(keychainRef)
    if result != 0:
        raise Exception('Error: Could not create keychain', result)
    if auto_search:
        add_keychain_search(keychain_name)

def delete_keychain(keychain_name):
    # For the time being here, dummy mode to keep from deleting login and System keychain
    full_name = resolve_keychain_name(keychain_name)
    if (full_name == resolve_keychain_name('login.keychain')):
        return
    if (full_name == '/Library/Keychains/System.keychain'):
        return
    keychainRef = OpaqueTypeRef()
    # Always succeeds, safe to ignore result
    result = Security.SecKeychainOpen(keychain_name, byref(keychainRef))
    result = Security.SecKeychainDelete(keychainRef)
    safe_release(keychainRef)
    if result != 0:
        raise Exception('Error: Could not delete keychain', result)

def keychain_import_cert(keychain_name, cert_path):
    # WARNING - ROUGH CODE, NO ERROR HANDLING YET
    # No trust model here, good for client certs - not for CAs
    # Yay, it works! - Still need to add error checking and result checking
    #
    # Read in the cert_path first
    cert_handle = open(cert_path, 'rb')
    cert_data   = cert_handle.read()
    cert_handle.close()
    # Create a CFData reference with it
    inData = CFDataCreate(None, cert_data, len(cert_data))
    # Get the keychain ref
    keychainRef = OpaqueTypeRef()
    result = Security.SecKeychainOpen(keychain_name, byref(keychainRef))
    keyParams = SecKeyImportExportParameters(0,0,None,None,None,None,0,0)
    keyParams.flags = kSecKeySecurePassphrase
    fileStr  = CFStringCreateWithCString(None, os.path.split(os.path.abspath(cert_path))[-1], kCFStringEncodingUTF8)
    dummyStr = CFStringCreateWithCString(None, "You should never see this, something went wrong.", kCFStringEncodingUTF8)
    keyParams.alertPrompt = dummyStr
    outArray = OpaqueTypeRef()
    result = Security.SecKeychainItemImport(inData, fileStr, None, None, 0, byref(keyParams), keychainRef, byref(outArray))
    # Cleanup
    safe_release(outArray)
    safe_release(fileStr)
    safe_release(dummyStr)
    safe_release(keychainRef)
    safe_release(inData)
    if result != 0:
        raise Exception('Error: Error importing certificate into keychain', result)

def keychain_add_trusted_cert(keychain_name, cert_path):
    # WARNING - ROUGH CODE, NO ERROR HANDLING YET
    # Yay, it works! - Still need to add error checking and result checking
    # When used as a user in graphical mode - will cause a GUI prompt
    # When used as root, for one of root's keychains - does not cause a GUI prompt
    domain = kSecTrustSettingsDomainUser
    trustSettings = None
    keychainRef = OpaqueTypeRef()
    result = Security.SecKeychainOpen(keychain_name, byref(keychainRef))
    # Going to assume PEM file for now
    certRef = OpaqueTypeRef()
    # readCertFile(certFile, byref(certRef))
    cert_handle = open(cert_path, 'rb')
    cert_data   = cert_handle.read()
    cert_handle.close()
    if not (('-----BEGIN ' in cert_data) and ('-----END ' in cert_data)):
        # isNotPem
        raise Exception('Error: Certificate does not appear to be .pem file')
    # Decode the base64 data
    core_data = cert_data.split('-----BEGIN ',1)[-1].replace('\r','\n').split('-----\n',1)[-1].split('\n-----END ',1)[0]
    core_data = ''.join(core_data.split('\n'))
    pem_data  = create_string_buffer(base64.b64decode(core_data), len(core_data))
    # Create the CSSM_DATA struct
    certData = CSSM_DATA(len(pem_data), addressof(pem_data))
    certRef = OpaqueTypeRef()
    result = Security.SecCertificateCreateFromData(byref(certData), CSSM_CERT_X_509v3, CSSM_CERT_ENCODING_DER, byref(certRef))
    # We're cooking with gas now
    result = Security.SecCertificateAddToKeychain(certRef, keychainRef)
    result = Security.SecTrustSettingsSetTrustSettings(certRef, domain, trustSettings)
    safe_release(certRef)
    safe_release(keychainRef)
