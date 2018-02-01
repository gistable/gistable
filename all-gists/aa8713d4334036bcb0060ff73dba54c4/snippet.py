#!/usr/bin/python

import objc, CoreFoundation, Foundation, sys

class attrdict(dict): 
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

NetFS = attrdict()
# Can cheat and provide 'None' for the identifier, it'll just use frameworkPath instead
# scan_classes=False means only add the contents of this Framework
NetFS_bundle = objc.initFrameworkWrapper('NetFS', frameworkIdentifier=None, frameworkPath=objc.pathForFramework('NetFS.framework'), globals=NetFS, scan_classes=False)

# https://developer.apple.com/library/mac/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/Articles/ocrtTypeEncodings.html
# Fix NetFSMountURLSync signature
del NetFS['NetFSMountURLSync']
objc.loadBundleFunctions(NetFS_bundle, NetFS, [('NetFSMountURLSync', 'i@@@@@@o^@')])

def mount_share(share_path):
    # Mounts a share at /Volumes, returns the mount point or raises an error
    sh_url = CoreFoundation.CFURLCreateWithString(None, share_path, None)
    # Set UI to reduced interaction
    open_options  = {NetFS.kNAUIOptionKey: NetFS.kNAUIOptionNoUI}
    # Allow mounting sub-directories of root shares
    mount_options = {NetFS.kNetFSAllowSubMountsKey: True}
    # Mount!
    result, output = NetFS.NetFSMountURLSync(sh_url, None, None, None, open_options, mount_options, None)
    # Check if it worked
    if result != 0:
         raise Exception('Error mounting url "%s": %s' % (share_path, output))
    # Return the mountpath
    return str(output[0])

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
    # Mount!
    result, output = NetFS.NetFSMountURLSync(sh_url, mo_url, None, None, open_options, mount_options, None)
    # Check if it worked
    if result != 0:
         raise Exception('Error mounting url "%s" at path "%s": %s' % (share_path, mount_path, output))
    # Return the mountpath
    return str(output[0])

def mount_share_with_credentials(share_path, username, password):
    # Mounts a share at /Volumes, returns the mount point or raises an error
    # Include username and password as parameters, not in the share_path URL
    sh_url = CoreFoundation.CFURLCreateWithString(None, share_path, None)
    # Set UI to reduced interaction
    open_options  = {NetFS.kNAUIOptionKey: NetFS.kNAUIOptionNoUI}
    # Allow mounting sub-directories of root shares
    mount_options = {NetFS.kNetFSAllowSubMountsKey: True}
    # Mount!
    result, output = NetFS.NetFSMountURLSync(sh_url, None, username, password, open_options, mount_options, None)
    # Check if it worked
    if result != 0:
         raise Exception('Error mounting url "%s": %s' % (share_path, output))
    # Return the mountpath
    return str(output[0])

def mount_share_at_path_with_credentials(share_path, mount_path, username, password):
    # Mounts a share at the specified path, returns the mount point or raises an error
    # Include username and password as parameters, not in the share_path URL
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
    # Mount!
    result, output = NetFS.NetFSMountURLSync(sh_url, mo_url, username, password, open_options, mount_options, None)
    # Check if it worked
    if result != 0:
         raise Exception('Error mounting url "%s" at path "%s": %s' % (share_path, mount_path, output))
    # Return the mountpath
    return str(output[0])

if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print "Usage: mount_shares_tool.py 'afp://servername/share' '/path/to/mount/at'"
    else:
        mount_share_at_path(sys.argv[1], sys.argv[2])