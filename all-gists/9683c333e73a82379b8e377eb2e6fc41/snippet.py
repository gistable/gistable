import struct, objc
from Foundation import NSBundle
from Cocoa import NSAppleEventDescriptor

def OSType(s):
    # Convert 4 character code into 4 byte integer
    return struct.unpack('>I', s)[0]

# Create an opaque pointer type to mask the raw AEDesc pointers we'll throw around
AEDescRef = objc.createOpaquePointerType('AEDescRef', '^{AEDesc=I^^{OpaqueAEDataStorageType}}')

# Load AESendMessage from AE.framework for sending the AppleEvent
AE_bundle = NSBundle.bundleWithIdentifier_('com.apple.AE')
functions = [("AESendMessage", b"i^{AEDesc=I^^{OpaqueAEDataStorageType}}^{AEDesc=I^^{OpaqueAEDataStorageType}}iq"),]
objc.loadBundleFunctions(AE_bundle, globals(), functions)

# defined in AEDataModel.h
kAENoReply            =  1
kAENeverInteract      = 16
kAEDefaultTimeout     = -1
kAnyTransactionID     =  0
kAutoGenerateReturnID = -1

# defined in AEDataModel.h
typeAppleEvent          = OSType('aevt')
typeApplicationBundleID = OSType('bund')

# defined in AERegistry.h
kAELogOut               = OSType('logo')
kAEReallyLogOut         = OSType('rlgo')
kAEShowRestartDialog    = OSType('rrst')
kAEShowShutdownDialog   = OSType('rsdn')

# Build a standalone application descriptor by bundle id
loginwindowDesc = NSAppleEventDescriptor.alloc().initWithDescriptorType_data_(typeApplicationBundleID, buffer('com.apple.loginwindow'))

# build an event descriptor with our app descriptor as the target and the kAELogOut eventID
event = NSAppleEventDescriptor.appleEventWithEventClass_eventID_targetDescriptor_returnID_transactionID_(
        typeAppleEvent, kAELogOut, loginwindowDesc, kAutoGenerateReturnID, kAnyTransactionID)
eventDesc = event.aeDesc()

# Send a polite logout (returns immediately)
err = AESendMessage(eventDesc, None, kAENoReply|kAENeverInteract, kAEDefaultTimeout)
