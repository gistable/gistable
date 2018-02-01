import objc
from Foundation import NSBundle

CG_bundle = NSBundle.bundleWithIdentifier_('com.apple.CoreGraphics')

functions = [("CGSSessionCopyAllSessionProperties", b"@"),]

objc.loadBundleFunctions(CG_bundle, globals(), functions)

# example usage: graphical_security_sessions = CGSSessionCopyAllSessionProperties()
# keys to look for:
#     kCGSessionLoginDoneKey  - set to 1 if user has logged in
#     kCGSSessionOnConsoleKey - set to 1 if user currently has console/graphical control
# 
# Example data:
# 
# >>> a = CGSSessionCopyAllSessionProperties()
# >>> a
# (
#         {
#         kCGSSessionAuditIDKey = 100409;
#         kCGSSessionGroupIDKey = 20;
#         kCGSSessionIDKey = 258;
#         kCGSSessionLoginwindowSafeLogin = 0;
#         kCGSSessionOnConsoleKey = 0;
#         kCGSSessionOrderingKey = 2;
#         kCGSSessionSystemSafeBoot = 0;
#         kCGSSessionUserIDKey = 503;
#         kCGSSessionUserNameKey = testnow;
#         kCGSessionLoginDoneKey = 1;
#         kCGSessionLongUserNameKey = testnow;
#         kSCSecuritySessionID = 100409;
#     },
#         {
#         kCGSSessionAuditIDKey = 100008;
#         kCGSSessionGroupIDKey = 20;
#         kCGSSessionIDKey = 257;
#         kCGSSessionLoginwindowSafeLogin = 0;
#         kCGSSessionOnConsoleKey = 1;
#         kCGSSessionOrderingKey = 1;
#         kCGSSessionSystemSafeBoot = 0;
#         kCGSSessionUserIDKey = 501;
#         kCGSSessionUserNameKey = mike;
#         kCGSessionLoginDoneKey = 1;
#         kCGSessionLongUserNameKey = mike;
#         kSCSecuritySessionID = 100008;
#     }
# )
