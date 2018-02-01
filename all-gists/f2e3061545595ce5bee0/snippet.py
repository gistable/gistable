# This code must run as root

# We're mixing ObjC and C-style dylibs, so this is really fun
# The only reason we're doing this is that the OS is _really really_ picky about trying to do
# ANYTHING with the CoreStorage Family Properties CFDictionary that's in-memory EXCEPT for
# making a mutable copy of it.

# Once we've done that, we can bring it into pyObjC to play nicely with the data.

import objc
from ctypes import util, cast, CDLL, create_string_buffer, c_void_p, c_char_p, c_int

# First we have to load CoreFoundation as a C function to work with libCoreStorage and get data

CFoundation  = CDLL(util.find_library('CoreFoundation'))
CCoreStorage = CDLL('/usr/lib/libCoreStorage.dylib')

# This is our doorway into the data
CoreStorageCopyFamilyPropertiesForMount = CCoreStorage.CoreStorageCopyFamilyPropertiesForMount
CoreStorageCopyFamilyPropertiesForMount.restype = c_void_p

# Just enough to let us copy the dictionary
CFDictionaryCreateMutableCopy          = CFoundation.CFDictionaryCreateMutableCopy
CFDictionaryCreateMutableCopy.argtypes = [c_void_p, c_int, c_void_p]
CFDictionaryCreateMutableCopy.restype  = c_void_p

# We need to pass in a C string (null terminated) UTF-8 encoded path to a FileVault2 encrypted volume (needs to be mounted path or /dev path)
root_volume = create_string_buffer((u"/").encode("UTF-8"))

# Then we can load up the FileVault2 information! :)
family_properties = CoreStorageCopyFamilyPropertiesForMount(root_volume)

# But before we can do ANYTHING with it, we need to make a mutable copy
fv2_CFDictRef = CFDictionaryCreateMutableCopy(0, 0, family_properties)

# But this is a ctypes CFDictionary pointer, which is boring to play with - let's bridge it to pyobjc!
# pyobjc can take a raw pointer to a (known) CF type and convert to the normal NS/CF/python objects
fv2_dict = objc.objc_object(c_void_p=fv2_CFDictRef)

# Yay, now you have data!
# >>> fv2_dict.keys()
# (
#     "com.apple.corestorage.lvf.sequence",
#     "com.apple.corestorage.lvf.groupUUID",
#     DefaultEncryptionContext,
#     "com.apple.corestorage.lvf.uuid",
#     PreviousEncryptionContext,
#     "com.apple.corestorage.lvf.revertState",
#     "com.apple.corestorage.lvf.encryption.type",
#     "com.apple.corestorage.lvf.encryption.status",
#     "com.apple.corestorage.lvf.encryption.context"
# )
# >>> fv2_dict['com.apple.corestorage.lvf.encryption.context'].keys()
# (
#     CryptoUsers,
#     LastUpdateTime,
#     WrappedVolumeKeys,
#     ConversionInfo
# )
# >>> len(fv2_dict['com.apple.corestorage.lvf.encryption.context']['CryptoUsers'])
# 3
# >>> fv2_dict['com.apple.corestorage.lvf.encryption.context']['CryptoUsers'][0].keys()
# (
#     PassphraseWrappedKEKStruct,
#     WrapVersion,
#     UserType,
#     UserNamesData,
#     UserIdent,
#     PassphraseHint,
#     KeyEncryptingKeyIdent,
#     UserFullName,
#     UserIcon,
#     EFILoginGraphics
# )
# >>> 
