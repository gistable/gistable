import objc
from Foundation import NSBundle

IOKit_bundle = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')

functions = [
             ("IORegistryEntryFromPath", b"II*"),
             ("IORegistryEntryCreateCFProperty", b"@I@@I"),
            ]

objc.loadBundleFunctions(IOKit_bundle, globals(), functions)

def nvram(keyname):
    raw = IORegistryEntryCreateCFProperty(IORegistryEntryFromPath(0, "IODeviceTree:/options"), keyname, None, 0)
    # This returns the raw bytes
    # For string values, this will be what you're looking for
    # For more complex/structured values, you may need to parse the bytes
    return raw.bytes().tobytes()

# example usage:
# Look up a macOS device serial number via nvram
def serialnumber():
    return nvram("4D1EDE05-38C7-4A6A-9CC6-4BCCA8B38C14:SSN")