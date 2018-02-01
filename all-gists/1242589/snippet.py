#!/usr/bin/python
#
# Payload free package to create a user on a 10.7 system.


import sys
import os
import re
import time
import subprocess
from Foundation import *


TARGET_DIR = sys.argv[3]
SCRIPT_DIR = os.path.join(sys.argv[1], "Contents", "Resources")

DEFAULT_GID = 20
DEFAULT_PICTURE = "/Library/User Pictures/Fun/Smack.tif"
DEFAULT_SHELL = "/bin/bash"
DEFAULT_HOME = "/Users/%u"


# FIXME: Remove dotdict and use standard notation.
class dotdict(dict):
    """Dot notation dictionary access."""
    
    def __getattr__(self, attr):
        return self[attr]
    
    __setattr__= dict.__setitem__
    
    __delattr__= dict.__delitem__
    

class CLUError(Exception):
    """Exception class for Create Lion User."""
    pass
    

def dscl(*args):
    """Execute dscl command on the target volume's local node.
    
    This is a convenience function to execute dscl commands using the
    following template:
    
        TARGET/usr/bin/dscl -f TARGET/var/db/dslocal/nodes/Default localonly <arg1> <arg2> <...>
    
    Examples:
    
        dscl("-search", "/Local/Target/Users", "UniqueID", "501")
        dscl("-create", "/Local/Target/Users/%s" % user.shortname, "RealName", user.RealName)
    
    dscl's return code, stdout, and stderr are returned in a tuple.
    CLUError is raised if dscl can't execute.
    """
    
    dscl_args = ["%s/usr/bin/dscl" % TARGET_DIR,
                 "-f",
                 "%s/var/db/dslocal/nodes/Default" % TARGET_DIR,
                 "localonly"]
    dscl_args.extend(args)
    
    try:
        p = subprocess.Popen(dscl_args,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        (out, err) = p.communicate()
    except OSError as e:
        raise CLUError(u"Couldn't execute dscl: %s" % str(e))
    
    return (p.returncode, out, err)
    

def check_os():
    """Raise a CLUError if OS version isn't 10.7 or higher."""
    
    defaults = NSUserDefaults.standardUserDefaults()
    defaults.addSuiteNamed_(os.path.join(TARGET_DIR, "System/Library/CoreServices/SystemVersion"))
    os_ver = defaults.stringForKey_("ProductVersion")
    if not os_ver or not os_ver.startswith("10."):
        raise CLUError(u"Unrecognized OS version.")
    os_minor = int(os_ver.split(".")[1])
    if os_minor < 7:
        raise CLUError(u"OS version check failed, 10.7+ required.")
    

class UserConfig(object):
    """Hold user configuration.
    
    A plist is read as the input configuration, and its values are checked.
    A user dictionary is populated from the configuration, or with default and
    calculated values.
    
    CLUErrors are raised if anything is wrong with the configuration.
    """
    
    def __init__(self, plist):
        """Initialize user configuration from a property list."""
        
        super(UserConfig, self).__init__()
        
        plist_data = NSData.dataWithContentsOfFile_(plist)
        self.conf, format, error = \
         NSPropertyListSerialization.propertyListFromData_mutabilityOption_format_errorDescription_(
                        plist_data, NSPropertyListMutableContainers, None, None)
        if error:
            raise CLUError(u"Couldn't read %s: %s" % (plist, error))
        
        # This dictionary will hold the new user we're creating. The check_*-
        # methods will read the configuration and populate it.
        self.user = dotdict()
        
    
    re_shortname = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]{0,30}$')
    
    def check_shortname(self):
        """shortname must be 1 to 31 alphanumeric characters, first is alpha."""
        
        if not "shortname" in self.conf:
            raise CLUError(u"A shortname must be provided.")
        if not self.re_shortname.search(self.conf["shortname"]):
            raise CLUError(u"Invalid shortname '%s'." % self.conf["shortname"])
        
        (ret, out, err) = dscl("-read", u"/Local/Target/Users/%s" % self.conf["shortname"])
        if ret == 0:
            raise CLUError(u"User %s already exists" % self.conf["shortname"])
        
        self.user.shortname = self.conf["shortname"]
        
    
    def check_realname(self):
        """Use a RealName if supplied, otherwise use shortname."""
        
        self.user.RealName = self.conf.get("RealName", self.user.shortname)
        
    
    def check_password(self):
        """Ensure a hashed password is provided."""
        
        if not "ShadowHashData" in self.conf:
            raise CLUError(u"ShadowHashData must be provided.")
        # TODO: Verify syntax of ShadowHashData.
        self.user.ShadowHashData = self.conf["ShadowHashData"]
        
    
    def check_uniqueid(self):
        """Use the supplied UID or find an unused UID between 501 and 600."""
        
        # Use the supplied UID if given.
        if "UniqueID" in self.conf:
            self.user.UniqueID = int(self.conf["UniqueID"])
            return
        
        # Otherwise we search for users with UIDs between 501 and 600.
        for uid in range(501, 601):
            (retcode, out, err) = dscl("-search",
                                       "/Local/Target/Users",
                                       "UniqueID",
                                       "%d" % uid)
            # Empty output from dscl means the UID is available.
            if not out:
                self.user.UniqueID = uid
                return
        
    
    def check_primarygroupid(self):
        """Use a PrimaryGroupID if supplied, otherwise use default."""
        
        self.user.PrimaryGroupID = int(self.conf.get("PrimaryGroupID", DEFAULT_GID))
        
    
    def check_picture(self):
        """Use a Picture if supplied, otherwise use default."""
        
        self.user.Picture = self.conf.get("Picture", DEFAULT_PICTURE)
        
    
    def check_usershell(self):
        """Use a UserShell if supplied, otherwise use default."""
        
        self.user.UserShell = self.conf.get("UserShell", DEFAULT_SHELL)
        
    
    def check_nfshomedirectory(self):
        """Use a NFSHomeDirectory if supplied, otherwise use default."""
        
        home = self.conf.get("NFSHomeDirectory", DEFAULT_HOME)
        home = re.sub(r'%u', self.user.shortname, home)
        home = re.sub(r'%n', "%d" % self.user.UniqueID, home)
        home = re.sub(r'%l', self.user.shortname[0].lower(), home)
        home = re.sub(r'%L', self.user.shortname[0].upper(), home)
        self.user.NFSHomeDirectory = home
        
    
    def check_generateduid(self):
        """Use a UUID if supplied."""
        
        self.user.GeneratedUID = self.conf.get("GeneratedUID", None)
        
    
    def check_isadmin(self):
        """Check if the user should be an administrator, default is no."""
        
        self.user.IsAdmin = self.conf.get("IsAdmin", False)
        
    
    def check_ishidden(self):
        """Check if the user should be hidden from the login window, default is no."""
        
        self.user.IsHidden = self.conf.get("IsHidden", False)
        
    
    def check_kickstartard(self):
        """Check if ARD should be kickstarted for the user."""
        
        self.user.KickstartARD = self.conf.get("KickstartARD", False)
        

# FIXME: Don't hardcode utf-8.
# TODO: Use logging instead.
def printenc(msg, stream=sys.stdout, encoding="utf-8"):
    print >>stream, msg.encode(encoding)
    

def printerr(msg):
    printenc(msg, sys.stderr)
    

def main(argv):
    
    #
    # Read configuration plist.
    #
    
    try:
        # Ensure we're running on 10.7+
        check_os()
        
        # Load the configuration.
        user_config = UserConfig(os.path.join(SCRIPT_DIR, "userdata.plist"))
        
        # Check the configuration.
        user_config.check_shortname()
        user_config.check_realname()
        user_config.check_password()
        user_config.check_uniqueid()
        user_config.check_primarygroupid()
        user_config.check_picture()
        user_config.check_usershell()
        user_config.check_nfshomedirectory()
        user_config.check_generateduid()
        user_config.check_isadmin()
        user_config.check_ishidden()
        user_config.check_kickstartard()
        
    except CLUError as e:
        printerr(str(e))
        return 1
    
    user = dotdict(user_config.user)
    
    #
    # Create the user using dscl.
    #
    
    printenc(u"Creating new user %s" % repr(user.shortname))
    
    user_path = "/Local/Target/Users/%s" % user.shortname
    
    # Bail out if we can't create the user at all.
    (ret, out, err) = dscl("-create", user_path)
    if ret:
        printerr(u"dscl: Creation of %s failed: %s" % (user_path, err))
        return 2
    
    # Wrap dscl calls to display any errors.
    def dscl_check(*args):
        (ret, out, err) = dscl(*args)
        if ret:
            printerr(u"dscl %s returned %d: %s" % (" ".join(args), ret, err))
    
    for a in ("RealName",
              "PrimaryGroupID",
              "UniqueID",
              "NFSHomeDirectory",
              "Picture",
              "UserShell"):
        printenc("%s: %s" % (a, repr(user[a])))
        dscl_check("-create", user_path, a, str(user[a]))
    
    if user.GeneratedUID:
        printenc("GeneratedUID: %s" % user.GeneratedUID)
        dscl_check("-create", user_path, "GeneratedUID", user.GeneratedUID)
    
    #
    # Set ShadowHashData by writing directly to the user plist.
    #
    
    printenc(u"Writing ShadowHashData")
    
    def flush_ds_cache():
        ret = subprocess.call(("/usr/bin/dscacheutil", "-flushcache"))
        if ret:
            printerr(u"Warning: dscacheutil -flushcache returned %d" % ret)
        time.sleep(5)
    
    # Start by flushing the ds cache as we're going to access the plist directly.
    flush_ds_cache()
    
    user_plist_path = os.path.join(TARGET_DIR, "var/db/dslocal/nodes/Default/users/%s.plist" % user.shortname)
    user_plist_data = NSData.dataWithContentsOfFile_(user_plist_path)
    if not user_plist_data:
        printerr(u"Can't read %s" % user_plist_path)
        return 2
    
    user_plist, plist_format, error = \
     NSPropertyListSerialization.propertyListFromData_mutabilityOption_format_errorDescription_(
                    user_plist_data, NSPropertyListMutableContainers, None, None)
    if error:
        printerr(u"Can't set ShadowHashData: %s" % error)
        return 2
    
    user_plist["ShadowHashData"] = user.ShadowHashData
    
    user_plist_data, error = \
     NSPropertyListSerialization.dataFromPropertyList_format_errorDescription_(
                            user_plist, plist_format, None)
    if error:
        printerr(u"Can't serialize user plist: %s" % error)
        return 2
    
    if not user_plist_data.writeToFile_atomically_(user_plist_path, True):
        printerr(u"Couldn't write %s" % user_plist_path)
        return 2
    
    # Flushing the ds cache again, hopefully allowing directory services to pick up the new hash.
    flush_ds_cache()
    
    #
    # Other user settings.
    #
    
    # Add to admin group.
    if user.IsAdmin:
        printenc(u"Making %s admin" % user.shortname)
        dscl_check("-merge", "/Local/Target/Groups/admin", "GroupMembership", user.shortname)
    
    # Hide user from login window.
    if user.IsHidden:
        printenc(u"Hiding %s from login window" % user.shortname)
        p = subprocess.Popen(("/usr/bin/defaults",
                              "write",
                              os.path.join(TARGET_DIR, "Library/Preferences/com.apple.loginwindow"),
                              "HiddenUsersList",
                              "-array-add",
                              user.shortname),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        (out, err) = p.communicate()
        if p.returncode:
            printerr(u"Couldn't hide %s from loginwindow: %s" % (user.shortname, err))

    # Kickstart ARD
    if user.KickstartARD:
        printenc(u"Kickstarting ARD - Step One")
        ret = subprocess.call((os.path.join(TARGET_DIR,
                                            "System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart"),
            "-activate",
            "-configure",
            "-allowAccessFor",
            "-specifiedUsers",
            "-targetdisk",
            TARGET_DIR))
        if ret:
            printerr(u"Warning: ARD kickstart returned %d" % ret)

    
    # Kickstart ARD
    if user.KickstartARD:
        printenc(u"Kickstarting ARD - Step Two")
        ret = subprocess.call((os.path.join(TARGET_DIR,
                                            "System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart"),
            "-activate",
            "-configure",
            "-access",
            "-on",
            "-users",
            user.shortname,
            "-privs",
            "-all",
            "-restart",
            "-agent",
            "-targetdisk",
            TARGET_DIR))
        if ret:
            printerr(u"Warning: ARD kickstart returned %d" % ret)
    
    return 0
    

if __name__ == '__main__':
    sys.exit(main(sys.argv))
    
