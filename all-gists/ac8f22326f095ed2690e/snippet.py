from Foundation import NSBundle

# Load the framework bundle by its identifier
Metadata_bundle = NSBundle.bundleWithIdentifier_("com.apple.Metadata")

# Can also use: bundleWithPath or bundleWithURL

# Load the variable aka constant from the framework into globals
# This says to load whatever "kMDSPreferencesName" is and the type should be "an NSObject" aka "figure it out"
# which ends up giving us a NSString which pyObjC bridges to a python string nicely
objc.loadBundleVariables(Metadata_bundle, globals(), [('kMDSPreferencesName', '@')])

# >>> kMDSPreferencesName
# u'com.apple.SpotlightServer'

# OMG wasn't that soooo much easier than using ctypes?
# https://gist.github.com/pudquick/8f65bb9b306f91eafdcc