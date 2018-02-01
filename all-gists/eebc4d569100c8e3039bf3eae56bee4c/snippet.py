from Foundation import NSBundle
import objc
CoreServices = NSBundle.bundleWithIdentifier_('com.apple.CoreServices')     

functions = [
             ('_LSCopyRunningApplicationArray', '@I'),
             ('_LSCopyApplicationInformation', '@I@@'),
            ]

constants = [
             ('_kLSApplicationTypeKey', '@'),
             ('_kLSApplicationForegroundTypeKey', '@'),
             ('_kLSDisplayNameKey', '@')
            ]

objc.loadBundleFunctions(CoreServices, globals(), functions)
objc.loadBundleVariables(CoreServices, globals(), constants)

apps = _LSCopyRunningApplicationArray(0xfffffffe)
app_infos = [_LSCopyApplicationInformation(0xffffffff, x, None) for x in apps]
visible_app_infos = [x for x in app_infos if x.get(_kLSApplicationTypeKey, None) == _kLSApplicationForegroundTypeKey]
visible_apps = sorted([x.get(_kLSDisplayNameKey) for x in visible_app_infos])