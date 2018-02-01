# Tested on 10.11
# Assumes your network is in a state to actually do the discovery and that you have
# automatic timezone discovery enabled in Date & Time and Location services enabled
# (Generally this means wifi enabled on your device and network stack is up)

# For enabling location services and auto, check Allister's work here:
# https://gist.github.com/arubdesu/b72585771a9f606ad800

from Foundation import NSBundle
TZPP = NSBundle.bundleWithPath_("/System/Library/PreferencePanes/DateAndTime.prefPane/Contents/Resources/TimeZone.prefPane")
TimeZonePref          = TZPP.classNamed_('TimeZonePref')
ATZAdminPrefererences = TZPP.classNamed_('ATZAdminPrefererences')

atzap  = ATZAdminPrefererences.defaultPreferences()
pref   = TimeZonePref.alloc().init()
atzap.addObserver_forKeyPath_options_context_(pref, "enabled", 0, 0)
result = pref._startAutoTimeZoneDaemon_(0x1)