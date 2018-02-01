#!/usr/bin/env python

"""
Example fabfile for PyMNtos September 2011 meeting.

some examples of usage:

$ fab -H somehost -- uname -a
$ fab -H somehost run:'uname -a'
$ fab -d example
$ fab -l somehost1,somehost2 example
$ fab -H somehost1,somehost2 example
$ fab -R web confirm example

http://docs.fabfile.org/
https://github.com/fabric/fabric

cf:  
"""

import sys
import fabric
from fabric.api import require, open_shell, task, env, get, put, hide, show, cd, lcd, local, run, sudo
from fabric.decorators import runs_once
from fabric.contrib.console import confirm
from fabric.utils import abort
from functools import wraps


## env, stick whatever you want in here.  It'll show up in jobs

## confirm first -- a useful decorator, explored later.
def confirm_first(func):
    """
    the first time the function is called, it will ask if you really want to
    run it, *if* env['confirm_first'] is on.
    """               
    @wraps(func)
    def decorated(*args, **kwargs):
        if not env.get('confirm_first',False):
            return func(*args,**kwargs)
        
        name = func.__name__
        W = "Confirm [ %s ] (and all further instances)?" % name
        if not hasattr(decorated, '_confirmed'):
            c = confirm(W)
            decorated._confirmed = c
            if c:  
                print "User confirmed."
        
        if getattr(decorated,'_confirmed'):
            return func(*args, **kwargs)
        else:
            abort("user decided not to run function [ %s ].  Aborting."  % name)
    
    return decorated


## once you use task, you need to *always use task*.  
## then nothing is 'task' decorated, fabric will expose *all callables*
@task
@confirm_first  # defined later.
def example():
    ''' tiny example command'''
    print env.host

@task
def uname():
    """ uname -a on the remote machine """
    run("uname -a")

# expose the safe commands (not reboot!)
get,put,run,sudo,local,open_shell=map(task,(get,put,run,sudo,local,open_shell))


## the official way of doing roles
env.roledefs = dict(
    web=['web03','otherweb_host'],
    backup=['backup1','us.backup2'],
)


## alternative to roledefs... do it dynamically!  object needs:
#  * get,  * len, * in 
def allhosts():
    return [ 'web01','web02','us-backup','us-web','china-web' ]

class RoleHostsGenerator(object):
    """ generator for the env.hosts dictionary"""
    def __init__(self):
        pass
    
    def __getitem__(self,key):
        l = [x for x in allhosts() if key in x]
        return l

    def __contains__(self,x):
        return bool(self[x])

env.roledefs = RoleHostsGenerator()


@task(alias='confirm')
@runs_once
def confirm_setup(dlm=' ',**kwargs):
    """ confirm the whole run before starting.  This must be the FIRST TASK on the cli to be effective! 

    Side-Effects:
        env['confirm_first'] = True  # enables the @confirm_first action
    """
    env['confirm_first'] = True
    print "will run on hosts:\n"
    print dlm.join(env.all_hosts)
    print "\n"
    if not confirm("host list acceptable (continue on to tasks)?"):
        abort("cancelled by user")



## more realistic fabric commands, from flask-tool 
#  at https://github.com/imlucas/flask-tool
@task
def make_tar():
    require('version')
    #local('tar -cf %s.tar.gz .' % (env.version), capture=False)
    local("git archive --format=tar --prefix=%(release)s/ %(branch)s | gzip -c > %(release)s.tar.gz" % {
        'release': env.version,
        'branch': env.branch,
        }
    )
    local('rm -fr %s' % env.version)

@task
def upload_tar():
    require('version', provided_by=[deploy])

    put('%s.tar.gz' % env.version, '%s/archives/' % env.app_dir)
    with cd(env.app_dir):
        with cd('versions'):
            run('tar -zxvf ../archives/%s.tar.gz ' % (env.version))
            
    local('rm %s.tar.gz' % env.version)

@task
def switch_to(version):
    """Switch the current (ie live) version"""
    require('hosts')
    require('app_dir')
    with cd(env.app_dir):
        if exists('versions/previous'):
            run('rm versions/previous')
    
        if exists('versions/current'):
            run('mv versions/current versions/previous')
        
        run('ln -s ../versions/%s versions/current' % version)
        with cd('versions/current'):
            run("mkdir logs")
            run("mkdir etc")

@task
def deploy():
    make_tar()
    upload_tar()
    switch_to(env.version)

@task
def start():
    with cd('%s/versions/current' % env.app_dir):
        run('supervisord')

@task
def stop():
    with cd('%s/versions/current' % env.app_dir):
        run('supervisorctl shutdown')

@task
def restart():
    with cd('%s/versions/current' % env.app_dir):
        run('supervisorctl restart ')

