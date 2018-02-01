from ctypes import CDLL, Structure, POINTER, c_void_p, byref
from ctypes.util import find_library
import objc

PrintCore   = CDLL('/System/Library/Frameworks/ApplicationServices.framework/Frameworks/PrintCore.framework/PrintCore')
CFoundation = CDLL(find_library('CoreFoundation'))

class OpaqueType(Structure):
    pass

OpaqueTypeRef = POINTER(OpaqueType)

CFArrayGetValueAtIndex            = CFoundation.CFArrayGetValueAtIndex
CFArrayGetValueAtIndex.restype    = OpaqueTypeRef
PMPrinterGetName                  = PrintCore.PMPrinterGetName
PMPrinterGetName.restype          = c_void_p
CFStringCreateWithCString         = CFoundation.CFStringCreateWithCString
CFStringCreateWithCString.restype = OpaqueTypeRef

def CFSTR(pystr):
    return CFStringCreateWithCString(None, pystr, 0)

kPMPPDDescriptionType = CFSTR('PMPPDDescriptionType')


def printer_list(PMServer=None):
    printerList = c_void_p()
    OSStatus = PrintCore.PMServerCreatePrinterList(PMServer, byref(printerList))
    printers = []
    aCount = CFoundation.CFArrayGetCount(printerList)
    for i in range(aCount):
        printers.append(CFArrayGetValueAtIndex(printerList, i))
    return printers

def make_and_model(pObj):
    makeAndModel = c_void_p()
    OSStatus = PrintCore.PMPrinterGetMakeAndModelName(pObj, byref(makeAndModel))
    return objc.objc_object(c_void_p=makeAndModel)

def device_uri(pObj):
    deviceURI = c_void_p()
    OSStatus = PrintCore.PMPrinterCopyDeviceURI(pObj, byref(deviceURI))
    # return deviceURI
    return objc.objc_object(c_void_p=deviceURI)

def printer_name(pObj):
    return objc.objc_object(c_void_p=PMPrinterGetName(pObj))

def ppd(pObj):
    ppd = c_void_p()
    # OSStatus PMPrinterCopyDescriptionURL ( PMPrinter printer, CFStringRef descriptionType, CFURLRef _Nullable *fileURL );
    OSStatus = PrintCore.PMPrinterCopyDescriptionURL(pObj, kPMPPDDescriptionType, byref(ppd))
    return objc.objc_object(c_void_p=ppd)
