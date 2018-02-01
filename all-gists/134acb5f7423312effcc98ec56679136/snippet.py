import objc
from Foundation import NSBundle

IOKit = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')

functions = [("IOServiceGetMatchingService", b"II@"),
             ("IOServiceMatching", b"@*"),
             ("IORegistryEntryCreateCFProperties", b"IIo^@@I"),
             ("IOPSCopyPowerSourcesByType", b"@I"),
             ("IOPSCopyPowerSourcesInfo", b"@"),
            ]

objc.loadBundleFunctions(IOKit, globals(), functions)

# matches information pulled by: pmset -g rawbatt
def raw_battery_dict():
    battery = IOServiceGetMatchingService(0, IOServiceMatching("AppleSmartBattery"))
    if (battery != 0):
        # we have a battery
        err, props = IORegistryEntryCreateCFProperties(battery, None, None, 0)
        return props

# matches information pulled by: pmset -g batt
def adjusted_battery_dict():
    try:
        battery = list(IOPSCopyPowerSourcesByType(0))[0]
    except:
        battery = 0
    if (battery != 0):
        # we have a battery
        return battery

def raw_battery_percent():
    d = raw_battery_dict()
    if d:
        curc = d['CurrentCapacity']
        maxc = d['MaxCapacity']
        perc = 100.*curc/maxc
        return perc

def adjusted_battery_percent():
    d = adjusted_battery_dict()
    if d:
        return d["Current Capacity"]
