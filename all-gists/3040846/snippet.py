# Copyright @ Bjarte Johansen 2012
# License: http://ljos.mit-license.org/

from AppKit import NSApplication, NSApp, NSWorkspace
from Foundation import NSObject, NSLog
from PyObjCTools import AppHelper
from Quartz import kCGWindowListOptionOnScreenOnly, kCGNullWindowID, CGWindowListCopyWindowInfo

class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        workspace = NSWorkspace.sharedWorkspace()
        activeApps = workspace.runningApplications()
        for app in activeApps:
            if app.isActive():
                options = kCGWindowListOptionOnScreenOnly
                windowList = CGWindowListCopyWindowInfo(options,
                                                        kCGNullWindowID)
                for window in windowList:
                    if window['kCGWindowOwnerName'] == app.localizedName():
                        NSLog('%@', window)
                        break
                break
        AppHelper.stopEventLoop()

def main():
    NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    NSApp().setDelegate_(delegate)
    AppHelper.runEventLoop()
    
if __name__ == '__main__':
    main()