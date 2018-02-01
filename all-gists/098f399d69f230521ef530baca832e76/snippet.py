# Tested on 10.11

# Note:
# The marketing information embedded in the ServerInformation.framework is not the same as what
# About This Mac displays - there are differences. 
#
# For example:
#     ServerInformation: 15" MacBook Pro with Retina display (Mid 2015)
#        About This Mac: MacBook Pro (Retina, 15-inch, Mid 2015)
#
# About This Mac will actually hit the internet API to perform the lookup,
# and then saves it locally for future use.

from Foundation import NSBundle
import xml.etree.ElementTree as ET
import urllib2

ServerInformation   = NSBundle.bundleWithPath_('/System/Library/PrivateFrameworks/ServerInformation.framework')
ServerCompatibility = NSBundle.bundleWithPath_('/System/Library/PrivateFrameworks/ServerCompatibility.framework')

ServerInformationComputerModelInfo = ServerInformation.classNamed_('ServerInformationComputerModelInfo')
SVCSystemInfo = ServerCompatibility.classNamed_('SVCSystemInfo')

info = SVCSystemInfo.currentSystemInfo()
extended_info = ServerInformationComputerModelInfo.attributesForModelIdentifier_(info.computerModelIdentifier())

if extended_info:
    # We don't have to hit the internet API, we have some marketing knowledge
    marketing_name = extended_info['marketingModel']
else:
    # Sadly we'll have to reach out
    API = urllib2.urlopen('http://support-sp.apple.com/sp/product?cc=' + info.serialNumber()[-4:])
    marketing_name = ET.fromstring(API.read()).find('configCode').text
    API.close()