#!/usr/bin/python
"""Enables location services, allows Maps and Timezone"""
import os
import platform
import subprocess
import sys
try:
    sys.path.append('/usr/local/munki/munkilib/')
    import FoundationPlist
except ImportError as error:
    print "Could not find FoundationPlist, are munkitools installed?"
    raise error
# Enter the frogor

def ioreg():
    """get UUID to find locationd plist with"""
    cmd = ['/usr/sbin/ioreg', '-rd1', '-c', 'IOPlatformExpertDevice']
    full_reg = subprocess.check_output(cmd)
    reg_list = full_reg.split('\n')
    for reg in reg_list:
        if reg.startswith('      "IOPlatformUUID"'):
            uuid = reg[26:-1]
    return uuid

def root_check():
    """check sudo"""
    if not os.geteuid() == 0:
        exit("This must be run with sudo")

def os_check():
    """Only QA'd on ElCap"""
    maj_os_vers = platform.mac_ver()[0].split('.')[1]
    if maj_os_vers != '11':
        exit("This tool only tested on 10.11")

def sysprefs_boxchk():
    """Enables location services in sysprefs globally"""
    uuid = ioreg()
    path_stub = "/private/var/db/locationd/Library/Preferences/ByHost/com.apple.locationd."
    das_plist = path_stub + uuid.strip() + ".plist"
    on_disk = FoundationPlist.readPlist(das_plist)
    val = on_disk.get('LocationServicesEnabled', None)
    if val != 1:
        on_disk['LocationServicesEnabled'] = 1
        FoundationPlist.writePlist(on_disk, das_plist)
        os.chown(das_plist, 205, 205)

def service_handler(action):
    """Loads or unloads System's location services launchd job"""
    launchctl = ['/bin/launchctl', action,
                 '/System/Library/LaunchDaemons/com.apple.locationd.plist']
    subprocess.check_output(launchctl)

def add_maps():
    """maps dict for clients.plist in locationd settings"""
    com_apl_maps = {} #"com.apple.Maps"
    com_apl_maps["Hide"] = 0
    com_apl_maps["Whitelisted"] = 0
    com_apl_maps["BundleId"] = "com.apple.Maps"
    com_apl_maps["BundlePath"] = "/Applications/Maps.app"
    com_apl_maps["Registered"] = ""
    com_apl_maps["Executable"] = "/Applications/Maps.app/Contents/MacOS/Maps"
    com_apl_maps["Requirement"] = 'identifier "com.apple.Maps" and anchor apple'
    com_apl_maps["Authorized"] = 1
    das_plist = '/private/var/db/locationd/clients.plist'
    clients_dict = FoundationPlist.readPlist(das_plist)
    clients_dict['com.apple.Maps'] = com_apl_maps
    FoundationPlist.writePlist(clients_dict, das_plist)
    os.chown(das_plist, 205, 205)

def autoset_timezone():
    """enable timezone based on current location"""
    das_plist = '/Library/Preferences/com.apple.timezone.auto.plist'
    enabler = FoundationPlist.readPlist(das_plist)
    val = enabler.get('Active')
    if val != 1:
        enabler['Active'] = 1
    FoundationPlist.writePlist(enabler, das_plist)


def main():
    """gimme some main"""
    root_check()
    os_check()
    service_handler('unload')
    sysprefs_boxchk()
    add_maps()
    service_handler('load')
    autoset_timezone()

if __name__ == '__main__':
    main()
