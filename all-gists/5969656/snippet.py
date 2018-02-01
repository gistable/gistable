#/usr/bin/env python
from LaunchServices import LSSetDefaultHandlerForURLScheme
from LaunchServices import LSSetDefaultRoleHandlerForContentType

# 0x00000002 = kLSRolesViewer
# see https://developer.apple.com/library/mac/#documentation/Carbon/Reference/LaunchServicesReference/Reference/reference.html#//apple_ref/c/tdef/LSRolesMask
LSSetDefaultRoleHandlerForContentType("public.html", 0x00000002, "com.operasoftware.operanext")
LSSetDefaultRoleHandlerForContentType("public.xhtml", 0x00000002, "com.operasoftware.operanext")
LSSetDefaultHandlerForURLScheme("http", "com.operasoftware.operanext")
LSSetDefaultHandlerForURLScheme("https", "com.operasoftware.operanext")