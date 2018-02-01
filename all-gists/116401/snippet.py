# -*- coding: utf-8 -*-
# django_pave.py - Run Django management commands with a Paver task.
#
# It’s simple really; just run `paver manage syncdb`, or
# `paver manage runserver`, or indeed any Django management command. You can
# also define Paver tasks which load the Django settings before execution.
#
# Copyright (c) 2009 Zachary Voase <zacharyvoase@me.com>
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from functools import wraps
import sys

from django.core import management as mgmt

from paver.easy import *

# When doing `from django_pave import *`, it will only import the `manage()`
# task and `@management` decorator.
__all__ = ['manage', 'management']


# The following hackery is necessary to make sure the entire `paver manage`
# command is shown as the program's name (instead of just `paver`).
OldOptionParser = mgmt.LaxOptionParser
class LaxOptionParser(mgmt.LaxOptionParser):
    def __init__(self, *args, **kwargs):
        kwargs['prog'] = 'paver manage'
        OldOptionParser.__init__(self, *args, **kwargs)
mgmt.LaxOptionParser = LaxOptionParser


# And this hackery stops paver from printing the customary '---> task_name'
# header at the beginning of all task output. This might seem purely cosmetic,
# but for Django tasks which rely on streaming output (such as `dumpdata`), it
# is actually necessary for the task to function properly.
class QuietTask(tasks.Task):
    
    """A task which doesn’t print '---> task_name'."""
    
    def __call__(self, *args, **kwargs):
        # Switch on `tasks.environment.quiet`, which prevents the header from
        # being printed.
        old_quiet = tasks.environment.quiet
        tasks.environment.quiet = True
        
        return_value = super(QuietTask, self).__call__(*args, **kwargs)
        
        # Restore the old value of `tasks.environment.quiet`.
        tasks.environment.quiet = old_quiet
        return return_value


def setup_settings():
    """Set up the Django environment."""
    
    try:
        environment.options.django
    except (AttributeError, KeyError):
        sys.path.append(path(tasks.environment.pavement.__file__).dirname())
        
        try:
            import settings
        except ImportError, exc:
            sys.stderr.write(
                'There was an error importing your Django settings module.\n'
                '\n' + repr(exc) + '\n')
            sys.exit(1)

        mgmt.setup_environ(settings)
        environment.options.django = settings


def management(function):
    
    """
    Simple decorator to load Django settings before a task is run.
    
    ``management`` is a decorator which should be used on tasks to make sure
    that the Django environment is loaded before the task begins executing.
    If your task accepts ``options``, the Django settings will be available
    as ``options.django``.
    """
    
    setup_settings()
    return function


@consume_args
@QuietTask
@management
def manage(options):
    
    """
    Run Django management commands.
    
    The ``manage`` task allows you to run any Django management command as if
    it were a paver task. To use it, instead of running ``python manage.py``
    just use ``paver manage`` instead. For example::
        
        paver manage syncdb
        paver manage dumpdata myappname
        paver manage runserver
    
    Et cetera.
    """
        
    utility = mgmt.ManagementUtility(['paver manage'] + options.args)
    # This is again so that the name of the program shows up as the whole
    #`paver manage` instead of just `paver`.
    utility.prog_name = 'paver manage'    
    utility.execute()
