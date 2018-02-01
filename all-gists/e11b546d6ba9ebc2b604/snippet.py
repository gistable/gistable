# This actually uses the same API call (NetFSMountURLSync) that AppleScript uses :D
# Note: As written, requires OS X 10.10+ / pyobjc 2.5.1+

import objc, CoreFoundation
from ctypes import c_void_p, pointer, cast

# The only reason I'm doing this the XML way is because I don't have a better way (yet)
# for correcting a function signature -after- it's already been imported.
# The problem is the last argument is a pointer to a CFArrayRef, which works out to a
# pointer to a pointer to a CFArray. pyobjc doesn't hadnle that much abstraction, so I created
# a custom opaque type 'CFArrayRefRef' and manually handle the conversion to/from pointer.

NetFS_bridgesupport = \
"""<?xml version='1.0'?>
<!DOCTYPE signatures SYSTEM "file://localhost/System/Library/DTDs/BridgeSupport.dtd">
<signatures version='1.0'>
<depends_on path='/System/Library/Frameworks/SystemConfiguration.framework'/>
<depends_on path='/System/Library/Frameworks/CoreFoundation.framework'/>
<depends_on path='/System/Library/Frameworks/DiskArbitration.framework'/>
<string_constant name='kNAUIOptionKey' nsstring='true' value='UIOption'/>
<string_constant name='kNAUIOptionNoUI' nsstring='true' value='NoUI'/>
<string_constant name='kNetFSAllowSubMountsKey' nsstring='true' value='AllowSubMounts'/>
<string_constant name='kNetFSMountAtMountDirKey' nsstring='true' value='MountAtMountDir'/>
<opaque name='CFArrayRefRef' type='^{CFArrayRefRef=}' />
<function name='NetFSMountURLSync'>
<arg type='^{__CFURL=}'/>
<arg type='^{__CFURL=}'/>
<arg type='^{__CFString=}'/>
<arg type='^{__CFString=}'/>
<arg type='^{__CFDictionary=}'/>
<arg type='^{__CFDictionary=}'/>
<arg type='^{CFArrayRefRef=}'/>
<retval type='i'/>
</function>
</signatures>"""

# This is fun - lets you refer dict keys like dict.keyname
class attrdict(dict): 
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

# Create 'NetFS' framework object from XML above
NetFS = attrdict()
objc.parseBridgeSupport(NetFS_bridgesupport, NetFS, objc.pathForFramework('NetFS.framework'))

class ArrayPair(object):
    def __init__(self):
        super(type(self), self).__init__()
        # Build a pointer to a null array (which OS X will replace anyways)
        self.cArray = pointer(c_void_p(None))
        # Now we cast it to our custom opaque type
        self.oArray = NetFS.CFArrayRefRef(c_void_p=cast(self.cArray, c_void_p))
    def contents(self):
        # Cast the pointer cArray now points to into a objc object (CFArray/NSArray here)
        return [str(x) for x in objc.objc_object(c_void_p=self.cArray.contents)]

def mount_share(share_path):
    # Mounts a share at /Volumes, returns the mount point or raises an error
    sh_url = CoreFoundation.CFURLCreateWithString(None, share_path, None)
    # Set UI to reduced interaction
    open_options  = {NetFS.kNAUIOptionKey: NetFS.kNAUIOptionNoUI}
    # Allow mounting sub-directories of root shares
    mount_options = {NetFS.kNetFSAllowSubMountsKey: True}
    # Build our connected pointers for our results
    mountpaths = ArrayPair()
    # Attempt to mount!
    output = NetFS.NetFSMountURLSync(sh_url, None, None, None, open_options, mount_options, mountpaths.oArray)
    # Check if it worked
    if output != 0:
        raise Exception('Error mounting url "%s": %s' % (share_path, output))
    # Oh cool, it worked - return the resulting mount point path
    return mountpaths.contents()[0]

def mount_share_at_path(share_path, mount_path):
    # Mounts a share at the specified path, returns the mount point or raises an error
    sh_url = CoreFoundation.CFURLCreateWithString(None, share_path, None)
    mo_url = CoreFoundation.CFURLCreateWithString(None, mount_path, None)
    # Set UI to reduced interaction
    open_options  = {NetFS.kNAUIOptionKey: NetFS.kNAUIOptionNoUI}
    # Allow mounting sub-directories of root shares
    # Also specify the share should be mounted directly at (not under) mount_path
    mount_options = {
                     NetFS.kNetFSAllowSubMountsKey: True,
                     NetFS.kNetFSMountAtMountDirKey: True,
                    }
    # Build our connected pointers for our results
    mountpaths = ArrayPair()
    # Attempt to mount!
    output = NetFS.NetFSMountURLSync(sh_url, mo_url, None, None, open_options, mount_options, mountpaths.oArray)
    # Check if it worked
    if output != 0:
        raise Exception('Error mounting url "%s" at path "%s": %s' % (share_path, mount_path, output))
    # Oh cool, it worked - return the resulting mount point path
    return mountpaths.contents()[0]

# Example usage:
mounted_at = mount_share('afp://server.local/sharename')
mounted_at = mount_share_at_path('afp://server2.local/moreshare', '/custom/mount/location')

