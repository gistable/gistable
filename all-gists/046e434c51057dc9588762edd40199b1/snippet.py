#!/usr/bin/python
# pylint: disable=E0611, E1101, E0602
''''Fix 802.1x When Using Config Profiles and PEAP-MSCHAPV2 or EAP-TLS'''
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# This script will find the system profile that is attached to one ethernet
# interface from our configuration profile and then copy it to all other
# ethernet interfaces so that other ethernet interfaces can be used instead
# of just the FirstActiveEthernet at time of profile installation. This issue
# is still an issue as of 10.12.3
#
# Joshua D. Miller - josh@psu.edu - The Pennsylvania State University
# Last Updated Friday March 21, 2017
#
# References
# https://gist.github.com/pudquick/8ad859f30438f3be149fe9751391d037
# https://gist.github.com/pudquick/4cf32c2b403bf0be23b268d6dd3cf803
# https://github.com/mosen/moobjc-framework-Security/blob/
# master/metadata/Security.fwinfo
# https://github.com/mosen/meap/blob/master/meap/eap8021x/_metadata.py
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# I'd like to give a very special thanks to Mosen who was so influencial
# in making this script a reality. Thank you so much for asssting with
# this project and it is my hope that this truly solves our 802.1x issue
# on the Mac side and allows us to move forward with the project. We
# decided to switch from EAP-TLS to PEAP-MSCHAPV2 because the user
# will still need a domain bound computer which can only be done by our
# IT Staff and will need the cert from our CA. This script does work with both
# protocols though
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from Foundation import NSBundle
from SystemConfiguration import (
    SCNetworkServiceCopyAll, SCNetworkInterfaceGetBSDName,
    SCNetworkInterfaceGetInterfaceType, SCNetworkServiceGetInterface,
    SCPreferencesCreate)
import objc


def ethernet_services(services):
    '''function will pull any en(x) device that is truly an ethernet
    Special Thanks to @mosen for this little function that gets
    the job done'''
    for service in services:
        interface = SCNetworkServiceGetInterface(service)
        if SCNetworkInterfaceGetInterfaceType(interface) == 'Ethernet':
            yield interface


def main():
    '''This function is very similar to our fix but instead of performing
    any systematic changes will read the information and report it to
    jamf as an extension attribute.'''
    eap8021x_bundle = NSBundle.bundleWithPath_(
        '/System/Library/PrivateFrameworks/EAP8021X.framework')

    # EAP Functions from @mosen's meap project (See above for link)
    eapol_functions = [
        ('EAPOLClientConfigurationGetTypeID', 'Q'),
        ('EAPOLClientProfileGetTypeID', 'Q'),
        ('EAPOLClientItemIDGetTypeID', 'Q'),
        ('EAPOLClientConfigurationCreate',
         '^{EAPOLClientConfigurationRef=}^{__CFAllocator=}'),
        ('EAPOLClientProfileGetUserDefinedName',
         '@^{EAPOLClientProfileRef=}'),
        ('EAPOLClientConfigurationGetSystemProfile',
         '^{EAPOLClientProfileRef=}'
         '^{EAPOLClientConfigurationRef=}@'),
        ('EAPOLClientConfigurationSetSystemProfile',
         'Z^{EAPOLClientConfigurationRef=}@'
         '^{EAPOLClientProfileRef=}'),
        ('EAPOLClientConfigurationSave',
         'Z^{EAPOLClientConfigurationRef=}')]

    objc.loadBundleFunctions(eap8021x_bundle, globals(), eapol_functions)

    # CF Types to be loaded also from @mosen's meap project
    cf_types = [
        ('EAPOLClientConfigurationRef',
         '^{EAPOLClientConfigurationRef=}',
         EAPOLClientConfigurationGetTypeID()),

        ('EAPOLClientProfileRef',
         '^{EAPOLClientProfileRef=}',
         EAPOLClientProfileGetTypeID()),

        ('EAPOLClientItemIDRef',
         '^{EAPOLClientItemIDRef=}',
         EAPOLClientItemIDGetTypeID()), ]

    for item in cf_types:
        objc.registerCFSignature(*item)

    # Define blank list to be used to gather EAPOL information on
    # Ethernet interfaces
    interface_list = []
    prefs = SCPreferencesCreate(None, "python", None)
    services = SCNetworkServiceCopyAll(prefs)

    # Poll through the interfaces and make a list of the true Ethernet
    # adapters on the system
    for interface in ethernet_services(services):
        interface_list.append(SCNetworkInterfaceGetBSDName(interface))

    # For loop to iterate through our Ethernet adapters and determine if they
    # have the system profile we are looking for and apply it to any other
    # Ethernet interfaces that don't have it applied. Change "Ethernet(COE)"
    # to whatever your 802.1x profile is called in Network Preferences.
    # Default in jamf is sadly "Network"
    for ethernet in interface_list:
        cfg = EAPOLClientConfigurationCreate(None)
        look_for_cfg = EAPOLClientConfigurationGetSystemProfile(cfg, ethernet)
        if look_for_cfg is not None:
            if EAPOLClientProfileGetUserDefinedName(
                    look_for_cfg) == 'Ethernet(COE)':
                for ethernet in interface_list:
                    if EAPOLClientConfigurationGetSystemProfile(
                            cfg, ethernet) == look_for_cfg:
                        continue
                    else:
                        EAPOLClientConfigurationSetSystemProfile(cfg, ethernet, look_for_cfg)
                        EAPOLClientConfigurationSave(cfg)


if __name__ == '__main__':
    main()
