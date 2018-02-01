"""
Copyright (c) 2009, Sean Creeley
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  * Redistributions of source code must retain the above copyright notice, this
      list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above copyright notice, 
      this list of conditions and the following disclaimer in the documentation 
      and/or other materials provided with the distribution.
  * Neither the name of the Optaros, Inc. nor the names of its contributors may 
      be used to endorse or promote products derived from this software without 
      specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT 
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, 
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
POSSIBILITY OF SUCH DAMAGE.

=============
DaemonCommand
=============

Django Management Command for starting a daemon.

Use
===

Simple use of daemon command::

    from daemonextension import DaemonCommand
    from django.conf import settings
    import os
    
    class Command(DaemonCommand):
        
        stdout = os.path.join(settings.DIRNAME, "log/cubbyscott.out")
        stderr = os.path.join(settings.DIRNAME, "log/cubbyscott.err")
        pidfile = os.path.join(settings.DIRNAME, "pid/cb_link.pid")
        
        def handle_daemon(self, *args, **options):
            from flopsy import Connection, Consumer
            consumer = Consumer(connection=Connection())
            consumer.declare(queue='links', 
                             exchange='cubbyscott', 
                             routing_key='importer', auto_delete=False)
            
            def message_callback(message):
                print 'Recieved: ' + message.body
                consumer.channel.basic_ack(message.delivery_tag)
            
            consumer.register(message_callback)
            
            consumer.wait()

call::

    python python manage.py linkconsumer
    
"""

from django.core.management.base import BaseCommand
from optparse import make_option

import daemon
from daemon import pidlockfile

class DaemonCommand(BaseCommand):
        
    option_list = BaseCommand.option_list + (
        make_option('--chroot_directory', action='store', dest='chroot_directory',
            help='Full path to a directory to set as the effective root directory of \
            the process.'),
        make_option('--working_directory', action='store', dest='working_directory',
            default="/",
            help='Full path of the working directory to which the process should \
            change on daemon start.'),
        make_option('--umask', action='store', dest='umask', default=0, type="int",
            help='File access creation mask ("umask") to set for the process on \
            daemon start.'),
        make_option('--pidfile', action='store', dest='pidfile',
            help='Context manager for a PID lock file. When the daemon context opens \
            and closes, it enters and exits the `pidfile` context manager.'),
        make_option('--detach_process', action='store', dest='detach_process', 
            help='If ``True``, detach the process context when opening the daemon \
            context; if ``False``, do not detach.'),
        make_option('--uid', action='store', dest='uid', 
            help='The user ID ("UID") value to switch the process to on daemon start.'),
        make_option('--gid', action='store', dest='gid', 
            help='The group ID ("GID") value to switch the process to on daemon start.'),
        make_option('--prevent_core', action='store', dest='prevent_core', default=True,
            help='If true, prevents the generation of core files, in order to avoid \
            leaking sensitive information from daemons run as `root`.'),
        make_option('--stdin', action='store', dest='stdin', 
            help='Standard In'),
        make_option('--stdout', action='store', dest='stdout',
            help='Standard Out'),
        make_option('--stderr', action='store', dest='stderr',
            help='Standard Error'),
    )
    help = 'Create a daemon'
    
    chroot_directory = None
    working_directory = '/'
    umask = 0
    detach_process = True
    prevent_core = True
    stdin = None
    stdout = None
    stderr = None
    pidfile = None
    uid = None
    gid = None    
    
    
    def get_option_value(self, options, name, expected=None):
        value = options.get(name)
        if value == expected:
            value = getattr(self, name)
        print name, ' ', value
        return value
    
    def handle(self, *args, **options):
        """
        Takes the options and starts a daemon context from them. 
        
        Example::
        
            python manage.py linkconsumer --pidfile=/var/run/cb_link.pid 
                --stdout=/var/log/cb/links.out --stderr=/var/log/cb/links.err
        
        """
        context = daemon.DaemonContext()
        
        context.chroot_directory = self.get_option_value(options, 'chroot_directory')
        context.working_directory = self.get_option_value(options, 'working_directory', '/')
        context.umask = self.get_option_value(options, 'umask', 0)
        context.detach_process = self.get_option_value(options, 'detach_process')
        context.prevent_core = self.get_option_value(options, 'prevent_core', True)
        
        #Get file objects
        stdin =  self.get_option_value(options, 'stdin')
        if stdin is not None:
            context.stdin = open(stdin, "r")
        
        stdout = self.get_option_value(options, 'stdout')
        if stdout is not None:
            context.stdout = open(stdout, "a+")
        
        stderr = self.get_option_value(options, 'stderr')
        if stderr is not None:
            context.stderr = open(stderr, "a+")  
        
        #Make pid lock file
        pidfile = self.get_option_value(options, 'pidfile')
        if pidfile is not None:
            context.pidfile=pidlockfile.PIDLockFile(pidfile)
        
        uid = self.get_option_value(options, 'uid')
        if uid is not None:
            context.uid = uid
        
        gid = self.get_option_value(options, 'gid')
        if gid is not None:
            context.gid = uid
        
        context.open()        
        
        self.handle_daemon(*args, **options)

    def handle_daemon(self, *args, **options):
        """
        Perform the command's actions in the given daemon context
        """
        raise NotImplementedError()