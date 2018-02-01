#!/usr/bin/env python
# LICENSE: MIT
# original: http://people.redhat.com/~rjones/virt-what/


import struct


def cpuHypervisorID():
    # we cannot (yet) use _cpuid because of the different
    # unpack format.
    HYPERVISOR_CPUID_LEAF = 0x40000000
    with open('/dev/cpu/0/cpuid', 'rb') as f:
        f.seek(HYPERVISOR_CPUID_LEAF)
        c = struct.unpack('I12s', f.read(16))
        return c[1].strip('\x00')


def cpuModelName():
    with open('/proc/cpuinfo', 'rt') as f:
        for line in f:
            if ':' in line:
                k, v = line.split(':', 1)
                k = k.strip()
                if k == 'model name':
                    return v.strip()
    return ''


def findHypervisor():
    name = ''
    try:
        hid = cpuHypervisorID()
        if hid == 'VMwareVMware':
            name = 'vmware'
        elif hid == 'Microsoft Hv':
            name = 'hyperv'
        elif hid == 'XenVMMXenVMM':
            name = 'xen'
        elif hid == 'KVMKVMKVM':
            name = 'kvm'
        elif 'QEMU' in cpuModelName():
            name = 'qemu'
    except:
        pass# TODO
    return name


if __name__ == '__main__':
    print findHypervisor() or 'bare metal'