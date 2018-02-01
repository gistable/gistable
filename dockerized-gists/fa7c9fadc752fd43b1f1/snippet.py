#!/usr/bin/env python
from fabric.api import env, local, cd, prompt, run, settings, sudo, task, prefix
from functools import wraps
import shutil
import tempfile

kwargs = {}
def ask(*args):
    def deco(task):
        @wraps(task)
        def wrapper():
            for k in args:
                if k not in kwargs:
                    answer = prompt(k + ":")
                    kwargs[k] = answer
            kwargs.update(env)
            return task(kwargs=kwargs)
        return wrapper
    return deco

@task
@ask('odoo_ref')
def build(kwargs=None):
    """Creates an instance of Odoo v7 easily. Odoo is huge, so please provide a local reference repo for quicker setup."""
    if kwargs.get('odoo_ref'):
        local("git submodule add -b 7.0 --reference %(odoo_ref)s https://github.com/odoo/odoo.git" % kwargs)
    else:
        local("git submodule add -b 7.0 https://github.com/odoo/odoo.git" % kwargs)
    local("curl https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.11.6.tar.gz | tar xzf -")
    local("/usr/bin/env python virtualenv-1.11.6/virtualenv.py --system-site-packages env")

    this_file = 'env/bin/activate_this.py'
    execfile(this_file, dict(__file__=this_file))
    local("pip install --process-dependency-links --allow-all-external --allow-unverified PIL odoo/")

@task
@ask('tag')
def update(kwargs=None):
    """Runs export, deploy and reload in single task."""
    export()
    deploy()
    reload()

@task
@ask('tag')
def export(kwargs=None):
    """Export your project into a single tarball for easily deployment. This will take care of all your submodules too."""
    tmpdir = kwargs['tempd'] = tempfile.mkdtemp()

    # create distribution archive
    local("git archive --format=tar %(tag)s|tar x -C %(tempd)s" % kwargs)
    local("git submodule foreach 'git archive --format=tar HEAD|tar x -C %(tempd)s/$path'" % kwargs)
    local("tar czf %(tag)s.tar.gz -C %(tempd)s ." % kwargs)
    shutil.rmtree(tmpdir)

@task
@ask('tag', 'conf')
def deploy(kwargs=None):
    """Trasfer project tarball to a remote host and replace the current instance with this."""
    # transfer tarball to destination
    local("scp %(tag)s.tar.gz %(user)s@%(host_string)s:~" % kwargs)

    # setup instance directory and relink current symlink to the instance directory
    run("mkdir %(tag)s; tar xzvf %(tag)s.tar.gz -C %(tag)s" % kwargs)
    run("rm %(tag)s.tar.gz" % kwargs)

    run("chmod 0755 %(tag)s" % kwargs)
    with settings(warn_only=True):
        run("cp -u current/my.conf %(tag)s/" % kwargs)

    # reuse existing virtualenv
    with cd("%(tag)s" % kwargs):
        run("ln -sf ../env .")

    run("rm current; ln -sf %(tag)s current" % kwargs)

@task
@ask('name')
def reload(kwargs=None):
    """Reload remote instance (using supervisor)."""
    sudo("supervisorctl restart %(name)s" % kwargs)

@task
@ask('tag', 'dbname', 'dbuser')
def backup(kwargs=None):
    """Backup your database."""
    sudo("createdb -T %(dbname)s --owner=nobody %(dbname)s_pre_%(tag)s" % kwargs, user="%(dbuser)s" % kwargs)