#!/usr/bin/python

import lldb
import os
import re
import subprocess
import fblldbbase as fb

def lldbcommands():
  return [ PrintToFile() ]

class PrintToFile(fb.FBCommand):
  def name(self):
    return 'pfile'

  def description(self):
    return 'Print an array to a file.'

  def args(self):
    return [ fb.FBCommandArgument(arg='pointer', type='void *', help='The pointer to the first element in the array.') ]

  def options(self):
    return [
      fb.FBCommandArgument(short='-t', long='--type', arg='type', type='string', default='int', help='The type of values contained in the array'),
      fb.FBCommandArgument(short='-c', long='--size', arg='size', type='int', default=100, help='The number of elements to print'),
      fb.FBCommandArgument(short='-f', long='--file', arg='file', type='string', default='/tmp/lldb_out.txt', help='The file to write the results to')
    ]

  def run(self, args, options):
    res = lldb.SBCommandReturnObject()
    interpreter = lldb.debugger.GetCommandInterpreter()
    command = 'memory read --force -t %s -c %s %s' % (options.type, options.size, args[0])
    interpreter.HandleCommand(command, res)
    if not res.Succeeded():
      return
    output = res.GetOutput()

    print 'Printing to \'%s\'' % options.file
    f = open(options.file, "w")

    for line in output.splitlines():
      match = re.search('.*\s=\s(.*)', line)
      if match:
        f.write(match.group(1) + '\n')
    f.close()
