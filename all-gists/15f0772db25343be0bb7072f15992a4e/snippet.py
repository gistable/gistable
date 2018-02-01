#!/usr/bin/env python3
import struct
import lief
from lief.MachO import LOAD_COMMAND_TYPES, HEADER_FLAGS


def check(filename):
  macho = lief.parse(filename)

  # check this?
  # nx = HEADER_FLAGS.ALLOW_STACK_EXECUTION not in macho.header.flags

  # PIE
  pie_enabled = HEADER_FLAGS.PIE in macho.header.flags

  # restrict segment for anti-debugging
  # ptrace looks hard to detect by pure static analytics
  restricted_segment = False
  for segment in macho.segments:
    if segment.name.lower() == '__restrict':
      restricted_segment = True
      break

  imported = macho.imported_functions

  # stack canary
  canary_enabled = '___stack_chk_fail' in imported and '___stack_chk_guard' in imported
  
  # ARC
  arc_enabled = '_objc_release' in imported

  # encrypted
  cryptid = 0
  for cmd in macho.commands:
    if cmd.command == LOAD_COMMAND_TYPES.ENCRYPTION_INFO:
      buf = bytearray(cmd.data)
      cmd, cmdsize, cryptoff, cryptsize, cryptid = struct.unpack('<IIIII', buf)
      break

    elif cmd.command == LOAD_COMMAND_TYPES.ENCRYPTION_INFO_64:
      buf = bytearray(cmd.data)
      cmd, cmdsize, cryptoff, cryptsize, cryptid, pad = struct.unpack('<IIIIII', buf)
      break

  encrypted = bool(cryptid)

  result = {
    'RESTRICT': restricted_segment,
    'CANARY': canary_enabled,
    'PIE': pie_enabled,
    'ARC': arc_enabled,
    'ENCRYPTED': encrypted,
  }

  for item in result.items():
    print('%s: %s' % item)


if __name__ == '__main__':
  import sys
  try:
    path = sys.argv[1]
    check(path)
  except KeyError:
    print('usage: check.py EXECUTABLE')
