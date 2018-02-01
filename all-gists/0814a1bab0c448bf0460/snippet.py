#!/usr/bin/env python                                                                                                                                               
# -*- coding: utf-8 -*-
import cmd

ASCII = """
 .-.                  .        .-. .   ..---..    .             .  
(   ) o               |       (   )|   ||    |    |           .'|  
 `-.  .  .--.--. .,-. | .-.    `-. |---||--- |    |      .    ._|  
(   ) |  |  |  | |   )|(.-'   (   )|   ||    |    |       \  /  |  
 `-'-' `-'  '  `-|`-' `-`--'   `-' '   ''---''---''---'    `' '---'
                 |                                                 
"""

class CLI(cmd.Cmd):

  def __init__(self):
    cmd.Cmd.__init__(self)
    self.prompt = 'SHELL >> '

  def onecmd(self, s):
    if s in ['quit', 'exit']:
      exit(0)
    else:
      print s

  def do_EOF(self, s):
    return True

  def default(self, line):
    return

try:
  cli = CLI()
  cli.cmdloop(ASCII)
except:
  print ''
  exit(0)