import _winreg as reg
import win32file


adapter_key = r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}'


def get_device_guid():
    with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, adapter_key) as adapters:
        try:
            for i in xrange(10000):
                key_name = reg.EnumKey(adapters, i)
                with reg.OpenKey(adapters, key_name) as adapter:
                    try:
                        component_id = reg.QueryValueEx(adapter, 'ComponentId')[0]
                        if component_id == 'tap0801':
                            return reg.QueryValueEx(adapter, 'NetCfgInstanceId')[0]
                    except WindowsError, err:
                        pass
        except WindowsError, err:
            pass

def CTL_CODE(device_type, function, method, access):
    return (device_type << 16) | (access << 14) | (function << 2) | method;

def TAP_CONTROL_CODE(request, method):
    return CTL_CODE(34, request, method, 0)

TAP_IOCTL_CONFIG_POINT_TO_POINT = TAP_CONTROL_CODE(5, 0)
TAP_IOCTL_SET_MEDIA_STATUS = TAP_CONTROL_CODE(6, 0)
TAP_IOCTL_CONFIG_TUN = TAP_CONTROL_CODE(10, 0)


if __name__ == '__main__':
    guid = get_device_guid()
    handle = win32file.CreateFile(r'\\.\Global\%s.tap' % guid,
                                  win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                  win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
                                  None, win32file.OPEN_EXISTING,
                                  win32file.FILE_ATTRIBUTE_SYSTEM, # | win32file.FILE_FLAG_OVERLAPPED,
                                  None)
    print(handle.handle)
    if False:
        win32file.DeviceIoControl(handle, TAP_IOCTL_CONFIG_POINT_TO_POINT,
                                  '\xc0\xa8\x11\x01\xc0\xa8\x11\x10', None);
    else:
        win32file.DeviceIoControl(handle, TAP_IOCTL_SET_MEDIA_STATUS, '\x01\x00\x00\x00', None)
        win32file.DeviceIoControl(handle, TAP_IOCTL_CONFIG_TUN,
                                  '\x0a\x03\x00\x01\x0a\x03\x00\x00\xff\xff\xff\x00', None)
    while True:
        l, p = win32file.ReadFile(handle, 2000)
        q = p[:12] + p[16:20] + p[12:16] + p[20:]
        win32file.WriteFile(handle, q)
        print(p, q)
    win32file.CloseHandle(handle)
