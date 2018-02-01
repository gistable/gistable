#!/usr/bin/python

# As written, this requires the following:
# - OS X 10.6+ (may not work in 10.10, haven't tested)
# - python 2.6 or 2.7 (for collections.namedtuple usage, should be fine as default python in 10.6 is 2.6)
# - pyObjC (as such, recommended to be used with native OS X python install)

# Only tested and confirmed to work against 10.9.5
# Run with root

import objc, ctypes.util, os.path, collections
from Foundation import NSOrderedSet

preferred_SSID    = 'This SSID Should Be First'
next_to_last_SSID = 'This SSID Should Be Next To Last'
last_SSID         = 'This SSID Should be Last'

def load_objc_framework(framework_name):
    # Utility function that loads a Framework bundle and creates a namedtuple where the attributes are the loaded classes from the Framework bundle
    loaded_classes = dict()
    framework_bundle = objc.loadBundle(framework_name, bundle_path=os.path.dirname(ctypes.util.find_library(framework_name)), module_globals=loaded_classes)
    return collections.namedtuple('AttributedFramework', loaded_classes.keys())(**loaded_classes)

# Load the CoreWLAN.framework (10.6+)
CoreWLAN = load_objc_framework('CoreWLAN')

# Load all available wifi interfaces
interfaces = dict()
for i in CoreWLAN.CWInterface.interfaceNames():
    interfaces[i] = CoreWLAN.CWInterface.interfaceWithName_(i)

# Repeat the configuration with every wifi interface
for i in interfaces.keys():
    # Grab a mutable copy of this interface's configuration
    configuration_copy = CoreWLAN.CWMutableConfiguration.alloc().initWithConfiguration_(interfaces[i].configuration())
    # Find all the preferred/remembered network profiles
    profiles = list(configuration_copy.networkProfiles())
    # Grab all the SSIDs, in order
    SSIDs = [x.ssid() for x in profiles]
    # Check to see if our preferred SSID is in the list
    if (preferred_SSID in SSIDs):
        # Apparently it is, so let's adjust the order
        # Profiles with matching SSIDs will move to the front, the rest will remain at the end
        # Order is preserved, example where 'ssid3' is preferred:
        #    Original: [ssid1, ssid2, ssid3, ssid4]
        #   New order: [ssid3, ssid1, ssid2, ssid4]
        profiles.sort(key=lambda x: x.ssid() == preferred_SSID, reverse=True)
        # Now we move next_to_last_SSID to the end
        profiles.sort(key=lambda x: x.ssid() == next_to_last_SSID, reverse=False)
        # Now we move last_SSID to the end (bumping next_to_last_SSID)
        profiles.sort(key=lambda x: x.ssid() == last_SSID, reverse=False)
        # Now we have to update the mutable configuration
        # First convert it back to a NSOrderedSet
        profile_set = NSOrderedSet.orderedSetWithArray_(profiles)
        # Then set/overwrite the configuration copy's networkProfiles
        configuration_copy.setNetworkProfiles_(profile_set)
        # Then update the network interface configuration
        result = interfaces[i].commitConfiguration_authorization_error_(configuration_copy, None, None)
