#!/usr/bin/python
#
# Copyright (c) 2013, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  - Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#  - Neither the name of Arista Networks nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Port auto-description
#
#    Version 2.0 8/8/2013
#    Written by: 
#       Mark Berly, Arista Networks
#
#    Revision history:
#       1.0 - initially written using native sysdb calls (deprecated) 
#       2.0 - rewritten using eAPI


"""
   DESCRIPTION
      Port auto-description tool automatically updates the port
      description of an interface based on the lldp neighbor
      information of the attached device.

   INSTALLATION
      In order to install this extension:
         - copy 'portAuto' to /mnt/flash
         - enable the Command API interface:

               management api http-commands
                  no shutdown

         - change SWITCH_IP, USERNAME and PASSWORD at the top of the
           script to the ones appropriate for your installation. If
           running locallty, use '127.0.0.1' for the IP.

      portAuto can then be started using any of the following methods:
          
      1 - Execute directly from bash (from the switch, or a remote
          switch/server running Python):

         (bash)# /mnt/flash/portAuto
         
      2 - Configure an alias on the switch:

         (config)# alias portAuto bash /mnt/flash/portAuto
         
      3 - Schedule a job on the switch:
   
          e.g.: In order to run portAuto every 12 hours, use:

         (config)# schedule portAuto interval 720 max-log-files 0
                   command bash sudo /mnt/flash/portAuto

      4 - Run at switch boot time by adding the following startup
          config:

         (config)# event-handler portAutoDescription
         (config)# trigger on-boot
         (config)# action bash /mnt/flash/portAuto
         (config)# asynchronous
         (config)# exit

         Note that in order for this to work, you will also have to
         enable the Command API interface in the startup-config (see
         above).

   COMPATIBILITY
      Version 2.0 has been developed and tested against EOS-4.12.0 and
      is using the Command API interface. Hence, it should maintain
      backward compatibility with future EOS releases.

  LIMITATIONS
      None known.
"""

from jsonrpclib import Server

#----------------------------------------------------------------
# Configuration section
#----------------------------------------------------------------
SWITCH_IP = '127.0.0.1'
USERNAME = 'test'
PASSWORD = 'test'
#----------------------------------------------------------------

def main():
   switch = Server( 'https://%s:%s@%s/command-api' % 
                    ( PASSWORD, USERNAME, SWITCH_IP ) )
   response = switch.runCmds( 1, [ 'show lldp neighbors' ] )
   neighborInfo = response[ 0 ][ 'lldpNeighbors' ]
   for i in neighborInfo :
      localIntf = i[ 'port' ]
      intfDesc = '*** Link to %s(%s)' % ( i[ 'neighborDevice' ], 
                                          i[ 'neighborPort' ] )
      rc = switch.runCmds( 1, [ 'enable',
                                'configure',
                                'interface %s' % ( localIntf ),
                                'description %s' % ( intfDesc ) ] )

if __name__ == '__main__':
   main()