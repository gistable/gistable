__all__ = (
    ####### Class Objects

    #CoGetClassObject - Normal, not wrapped
    'CoDllGetClassObject', #Get ClassObject from a DLL file

    ####### ClassFactory::CreateInstance Wrappers

    'CoCreateInstanceFromFactory', #Create an object via IClassFactory::CreateInstance
    'CoCreateInstanceFromFactoryLicenced', #Create a licenced object via IClassFactory2::CreateInstanceLic

    ###### Util

    'CoReleaseObject', #Calls Release() on a COM object

    ###### Main Utility Methods

    #'CoCreateInstance', #Not wrapped, normal call
    'CoCreateInstanceLicenced', #CoCreateInstance, but with a licence key

    ###### Hacky DLL methods for reg-free COM without Activation Contexts, manifests, etc
    'CoCreateInstanceFromDll', #Given a dll, a clsid, and an iid, create an object
    'CoCreateInstanceFromDllLicenced', #Given a dll, a clsid, an iid, and a license key, create an object
)

IID_IClassFactory2 = "{B196B28F-BAB4-101A-B69C-00AA00341D07}"

from uuid import UUID
from ctypes import OleDLL, WinDLL, c_ulong, byref, WINFUNCTYPE, POINTER, c_char_p, c_void_p
from ctypes.wintypes import HRESULT
import pythoncom
import win32com.client

import logging
log = logging.getLogger(__name__)


def _raw_guid(guid):
    """Given a string GUID, or a pythoncom IID, return the GUID laid out in memory suitable for passing to ctypes"""
    return UUID(str(guid)).bytes_le

proto_icf2_base = WINFUNCTYPE(HRESULT,
    c_ulong,
    c_ulong,
    c_char_p,
    c_ulong,
    POINTER(c_ulong),
)
IClassFactory2__CreateInstanceLic = proto_icf2_base(7, 'CreateInstanceLic', (
    (1, 'pUnkOuter'),
    (1 | 4, 'pUnkReserved'),
    (1, 'riid'),
    (1, 'bstrKey'),
    (2, 'ppvObj'),
    ), _raw_guid(IID_IClassFactory2))

#--------------------------------
#--------------------------------

def _pc_wrap(iptr, resultCLSID=None):
    #return win32com.client.__WrapDispatch(iptr)
    log.debug("_pc_wrap: %s, %s"%(iptr, resultCLSID))
    disp = win32com.client.Dispatch(iptr, resultCLSID=resultCLSID)
    log.debug("_pc_wrap: %s (%s)", disp.__class__.__name__, disp)
    return disp

def CoCreateInstanceFromFactory(factory_ptr, iid_interface=pythoncom.IID_IDispatch, pUnkOuter=None):
    """Given a factory_ptr whose interface is IClassFactory, create the instance of clsid_class with the specified interface"""
    ClassFactory = pythoncom.ObjectFromAddress(factory_ptr.value, pythoncom.IID_IClassFactory)
    i = ClassFactory.CreateInstance(pUnkOuter, iid_interface)
    return i

def CoCreateInstanceFromFactoryLicenced(factory_ptr, key, iid_interface=pythoncom.IID_IDispatch, pUnkOuter=None):
    """Given a factory_ptr whose interface is IClassFactory2, create the instance of clsid_class with the specified interface"""
    requested_iid = _raw_guid(iid_interface)

    ole_aut = WinDLL("OleAut32.dll")
    key_bstr = ole_aut.SysAllocString(unicode(key))
    try:
        obj = IClassFactory2__CreateInstanceLic(factory_ptr, pUnkOuter or 0, c_char_p(requested_iid), key_bstr)
        disp_obj = pythoncom.ObjectFromAddress(obj, iid_interface)
        return disp_obj
    finally:
        if key_bstr:
            ole_aut.SysFreeString(key_bstr)

#----------------------------------

def CoReleaseObject(obj_ptr):
    """Calls Release() on a COM object. obj_ptr should be a c_void_p"""
    if not obj_ptr:
        return
    IUnknown__Release = WINFUNCTYPE(HRESULT)(2, 'Release', (), pythoncom.IID_IUnknown)
    IUnknown__Release(obj_ptr)

#-----------------------------------

def CoCreateInstanceLicenced(clsid_class, key, pythoncom_iid_interface=pythoncom.IID_IDispatch, dwClsContext=pythoncom.CLSCTX_SERVER, pythoncom_wrapdisp=True, wrapas=None):
    """Uses IClassFactory2::CreateInstanceLic to create a COM object given a licence key."""
    IID_IClassFactory2 = "{B196B28F-BAB4-101A-B69C-00AA00341D07}"
    ole = OleDLL("Ole32.dll")
    clsid_class_raw = _raw_guid(clsid_class)
    iclassfactory2 = _raw_guid(IID_IClassFactory2)
    com_classfactory = c_void_p(0)

    ole.CoGetClassObject(clsid_class_raw, dwClsContext, None, iclassfactory2, byref(com_classfactory))
    try:
        iptr = CoCreateInstanceFromFactoryLicenced(
                factory_ptr = com_classfactory,
                key=key,
                iid_interface=pythoncom_iid_interface,
                pUnkOuter=None,
        )
        if pythoncom_wrapdisp:
            return _pc_wrap(iptr, resultCLSID=wrapas or clsid_class)
        return iptr
    finally:
        if com_classfactory:
            CoReleaseObject(com_classfactory)

#-----------------------------------------------------------
#DLLs

def CoDllGetClassObject(dll_filename, clsid_class, iid_factory=pythoncom.IID_IClassFactory):
    """Given a DLL filename and a desired class, return the factory for that class (as a c_void_p)"""
    dll = OleDLL(dll_filename)
    clsid_class = _raw_guid(clsid_class)
    iclassfactory = _raw_guid(iid_factory)
    com_classfactory = c_void_p(0)
    dll.DllGetClassObject(clsid_class, iclassfactory, byref(com_classfactory))
    return com_classfactory

def CoCreateInstanceFromDll(dll, clsid_class, iid_interface=pythoncom.IID_IDispatch, pythoncom_wrapdisp=True, wrapas=None):
    iclassfactory_ptr = CoDllGetClassObject(dll, clsid_class)
    try:
        iptr = CoCreateInstanceFromFactory(iclassfactory_ptr, iid_interface)
        if pythoncom_wrapdisp:
            return _pc_wrap(iptr, resultCLSID=wrapas or clsid_class)
        return iptr
    finally:
        CoReleaseObject(iclassfactory_ptr)

def CoCreateInstanceFromDllLicenced(dll, clsid_class, key, iid_interface=pythoncom.IID_IDispatch, pythoncom_wrapdisp=True, wrapas=None):
    iclassfactory2_ptr = CoDllGetClassObject(dll, clsid_class, iid_factory=IID_IClassFactory2)
    try:
        iptr = CoCreateInstanceFromFactoryLicenced(iclassfactory2_ptr, key, iid_interface)
        if pythoncom_wrapdisp:
            return _pc_wrap(iptr, resultCLSID=wrapas or clsid_class)
        return iptr
    finally:
        CoReleaseObject(iclassfactory2_ptr)