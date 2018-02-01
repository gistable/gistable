#!/usr/bin/env python

import r2pipe

r2 = r2pipe.open('http://192.168.100.64:1337')


def cont():
    print(r2.cmd('dc'))


def step_out():
    print(r2.cmd('dcr; ds'))


def breakpoint(addr):
    print(r2.cmd('db ' + addr))


def get_esp():
    return r2.cmdj('drj')['esp']


def get_eip():
    return r2.cmdj('drj')['eip']


print('Starting debugging')
print(r2.cmd('doo'))
cont()
breakpoint('entry0')
print('Breakpoints:\n%s' % r2.cmd('db'))
cont()
print('Hit breakpoint at: %s' % r2.cmd('s'))

r2.cmd('aaa')

VirtualAlloc = int(r2.cmd('? [sym.imp.KERNEL32.dll_VirtualAlloc]~[0]'))
print('VirtualAlloc is at: ' + str(hex(VirtualAlloc)))
print('Current addr: ' + str(hex(get_eip())))

breakpoint('[sym.imp.KERNEL32.dll_VirtualAlloc]')  # Break on VirtualAlloc
print('Breakpoints:\n%s' % r2.cmd('db'))

while True:
    cont()
    print('Hit breakpoint at: %s' % r2.cmd('s'))
    eip = get_eip()
    if eip == VirtualAlloc:
        print('Break in VirtualAlloc')
        esp = get_esp()
        allocated_size = int(r2.cmd('pv @ 0x%x' % (esp + 8)), 16)
        step_out()  # step out of VirtualAlloc
        last_allocated_memory = r2.cmdj('drj')['eax']
        print('VirtualAlloc allocated 0x%x bytes of memory at 0x%x' % (allocated_size, last_allocated_memory))

        step_out()
        if r2.cmd('p8 2 @ 0x%x' % last_allocated_memory) == '4d5a':
            print('Found PE header at 0x%x' % last_allocated_memory)
            print(r2.cmd('wt dump.bin 0x%x @ 0x%x' % (allocated_size, last_allocated_memory)))
            print('PE dumped to dump.bin in %s' % r2.cmd('pwd'))
            quit()
