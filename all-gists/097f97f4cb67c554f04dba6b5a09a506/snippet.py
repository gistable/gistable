import objc
from Foundation import NSBundle
login_bundle = NSBundle.bundleWithPath_('/System/Library/PrivateFrameworks/login.framework')

functions = [('SACLockScreenImmediate', '@'),]
objc.loadBundleFunctions(login_bundle, globals(), functions)


# Lock the screen regardless of security settings or who is logged in
result = SACLockScreenImmediate()