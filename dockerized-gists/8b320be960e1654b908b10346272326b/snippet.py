# An overly complicated SIP config checker

# This is a technically interesting implementation because it does not rely on csrutil
# Instead it queries the kernel directly for the current configuration status
# This means, for example, in environments where SIP has been disabled and csrutil has
# been removed or modified (say, with DYLD_LIBRARY_PATH), as long as python can run you
# can still check status

# Additionally, checking the nvram csr-active-config setting isn't accurate now with
# 10.12.2+, since running "sudo csrutil clear" deletes the variable until reboot,
# leaving only the kernel itself understanding the current SIP state

# Examples of usage at the bottom

from ctypes import CDLL, c_uint, byref

# from xnu/bsd/sys/csr.h

CSR_VALID_FLAGS = [
    ('CSR_ALLOW_UNTRUSTED_KEXTS',      'kext',       '',              'Kext Signing',                       1 << 0),
    ('CSR_ALLOW_UNRESTRICTED_FS',      'fs',         '',              'Filesystem Protection',              1 << 1),
    ('CSR_ALLOW_TASK_FOR_PID',         'debug',      '',              'Debugging Restrictions',             1 << 2),
    ('CSR_ALLOW_KERNEL_DEBUGGER',      '',           '',              '<<CSR_ALLOW_KERNEL_DEBUGGER>>',      1 << 3),
    ('CSR_ALLOW_APPLE_INTERNAL',       '',           '--no-internal', 'Apple Internal',                     1 << 4),
    ('CSR_ALLOW_UNRESTRICTED_DTRACE',  'dtrace',     '',              'DTrace Restrictions',                1 << 5),
    ('CSR_ALLOW_UNRESTRICTED_NVRAM',   'nvram',      '',              'NVRAM Protections',                  1 << 6),
    ('CSR_ALLOW_DEVICE_CONFIGURATION', '',           '',              '<<CSR_ALLOW_DEVICE_CONFIGURATION>>', 1 << 7),
    ('CSR_ALLOW_ANY_RECOVERY_OS',      'basesystem', '',              'BaseSystem Verification',            1 << 8),
]

SIP_DISABLED = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 5) | (1 << 6)

class SIPSetting(object):
    def __init__(self, sip_flag_info, status=True):
        super(SIPSetting, self).__init__()
        self.define      = sip_flag_info[0]
        self.without     = sip_flag_info[1]
        self.force_off   = sip_flag_info[2]
        self.description = sip_flag_info[3]
        self.bitmask     = sip_flag_info[4]
        self.disabled     = status
    @property
    def enabled(self):
        return not self.disabled
    def __str__(self):
        if self.disabled is True:
            status = "disabled"
        else:
            status = "enabled"
        return "%s: %s" % (self.description, status)
    def __repr__(self):
        return self.__str__()
    def __nonzero__(self):
        return self.disabled
    def __eq__(self, value):
        return self.disabled == value

class SIPConfig(object):
    def __init__(self):
        super(SIPConfig, self).__init__()
        libsys = CDLL('/usr/lib/libSystem.dylib')
        raw    = c_uint(0)
        errmsg = libsys.csr_get_active_config(byref(raw))
        self.csr_active_config = raw.value
        self.csr_bitmask_str   =  "{0:b}".format(raw.value).zfill(16)
        self.key_order = [x[0] for x in CSR_VALID_FLAGS]
        self.config_dict = dict()
        self.full_config = list()
        self.enabled_config = list()
        for i in CSR_VALID_FLAGS:
            k, n, d, s, b = i
            # determine if this flag is set
            if (b & self.csr_active_config):
                s_obj = SIPSetting(i, status=True)
                self.enabled_config.append(s_obj)
            else:
                s_obj = SIPSetting(i, status=False)
            self.full_config.append(s_obj)
            self.config_dict[s_obj.define] = s_obj
            if (s_obj.without != ''):
                self.config_dict[s_obj.without] = s_obj
    @property
    def disabled(self):
        if ((self.csr_active_config & SIP_DISABLED) == SIP_DISABLED):
            return True
        return False
    @property
    def enabled(self):
        return not self.disabled
    @property
    def status(self):
        if self.enabled:
            return 'enabled'
        else:
            return 'disabled'
    def __getattr__(self, attr):
        return self.config_dict.__getitem__(attr)
    def __getitem__(self, item):
        if isinstance(item, (int, long, list, slice)):
            return self.enabled_config.__getitem__(item)
        else:
            return self.config_dict[item]
    def __repr__(self):
        return self.enabled_config.__repr__()

# Example usages:
# ---------------

# >>> sip = SIPConfig()
# >>> sip.status
# 'enabled'
# >>> sip.enabled
# True
# >>> sip.disabled
# False

# >>> sip
# [Debugging Restrictions: disabled, DTrace Restrictions: disabled]

# This is a custom configuration with dtrace and debug disabled
# Lots of different ways to reference the settings

# >>> sip.fs
# Filesystem Protection: enabled
# >>> sip['fs']
# Filesystem Protection: enabled
# >>> sip.fs.enabled
# True
# >>> sip.fs.disabled
# False

# >>> sip['CSR_ALLOW_UNTRUSTED_KEXTS']
# Kext Signing: enabled
# >>> sip.CSR_ALLOW_UNTRUSTED_KEXTS
# Kext Signing: enabled
# >>> sip.kext
# Kext Signing: enabled
# >>> sip.kext.define
# 'CSR_ALLOW_UNTRUSTED_KEXTS'
# >>> sip.kext.without
# 'kext'
# >>> sip.kext.description
# 'Kext Signing'
# >>> sip.kext.bitmask
# 1
# >>> sip.kext.disabled
# False

# Individual attributes boolean evaluate to "is the protection disabled"
# example: Is the filesystem protection disabled?
# >>> 'fs protection is disabled' if sip.fs else 'fs protection is enabled'
# 'fs protection is enabled'

# If you want to see all of the settings
# >>> sip.full_config
# [Kext Signing: enabled, Filesystem Protection: enabled, Debugging Restrictions: disabled, <<CSR_ALLOW_KERNEL_DEBUGGER>>: enabled, Apple Internal: enabled, DTrace Restrictions: disabled, NVRAM Protections: enabled, <<CSR_ALLOW_DEVICE_CONFIGURATION>>: enabled, BaseSystem Verification: enabled]
# >>> sip.csr_active_config
# 36L
# >>> sip.csr_bitmask_str
# '0000000000100100'
