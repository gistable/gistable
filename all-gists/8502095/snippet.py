from fabric.api import local, env, run, roles, execute, put
from fabric.utils import abort

env.user = "playuser"
env.roledefs = {
    'web': ['web.example.com'],
    'batch': ['batch.example.com']
}
env.num_of_releases = 3

def common_package():
    local("play projectfoo-bgtasks/package projectfoo-website/stage")

def common_releases():
    env.releases = sorted(run('ls -x %(releases_path)s' % { 'releases_path':env.releases_path }).split())
    if len(env.releases) >= 1:
        env.current_revision = env.releases[-1]
        env.current_release = "%(releases_path)s/%(current_revision)s" % { 'releases_path':env.releases_path, 'current_revision':env.current_revision }
    if len(env.releases) > 1:
        env.previous_revision = env.releases[-2]
        env.previous_release = "%(releases_path)s/%(previous_revision)s" % { 'releases_path':env.releases_path, 'previous_revision':env.previous_revision }

def common_symlink():
    if not env.has_key('current_release'):
        execute(common_releases)
    run("ln -nfs %(current_release)s %(current_path)s" % { 'current_release':env.current_release, 'current_path':env.current_path })

def common_cleanup():
    """Clean up old releases"""
    if not env.has_key('releases'):
        execute(common_releases)
    if len(env.releases) > env.num_of_releases:
        directories = env.releases
        directories.reverse()
        del directories[:env.num_of_releases]
        env.directories = ' '.join([ "%(releases_path)s/%(release)s" % { 'releases_path':env.releases_path, 'release':release } for release in directories ])
        run("rm -rf %(directories)s" % { 'directories':env.directories })

@roles('batch')
def batch_env():
    env.base_dir = "/home/playuser/bgtasks"
    env.packages = ["modules/bgtasks/target/scala-2.10/projectfoo-bgtasks_2.10-0.1-SNAPSHOT.jar", "target/universal/stage/lib/projectfoo-common.projectfoo-common-1.0-SNAPSHOT.jar"]

    env.current_path = "%(base_dir)s/current" % { 'base_dir':env.base_dir }
    env.releases_path = "%(base_dir)s/releases" % { 'base_dir':env.base_dir }
    env.shared_path = "%(base_dir)s/shared" % { 'base_dir':env.base_dir }

@roles('web')
def web_env():
    env.base_dir = "/home/playuser"
    env.packages = ["target/universal/stage/lib/projectfoo-website.projectfoo-website-1.0-SNAPSHOT.jar", "target/universal/stage/lib/projectfoo-common.projectfoo-common-1.0-SNAPSHOT.jar"]

    env.current_path = "%(base_dir)s/current" % { 'base_dir':env.base_dir }
    env.releases_path = "%(base_dir)s/releases" % { 'base_dir':env.base_dir }
    env.shared_path = "%(base_dir)s/shared" % { 'base_dir':env.base_dir }

@roles('batch')
def batch_setup():
    run("mkdir -p %(base_dir)s/{releases,shared}" % { 'base_dir':env.base_dir })
    run("mkdir -p %(shared_path)s/{conf,log,lib}" % { 'shared_path':env.shared_path })

@roles('web')
def web_setup():
    run("mkdir -p %(base_dir)s/{releases,shared}" % { 'base_dir':env.base_dir })
    run("mkdir -p %(shared_path)s/{conf,logs,lib}" % { 'shared_path':env.shared_path })


@roles('batch')
def batch_deploy():
    execute(batch_env)
    execute(batch_setup)
    execute(common_deploy)
    execute(common_symlink)
    execute(common_cleanup)

def common_deploy():
    if not env.has_key('releases_path') or not env.has_key('packages'):
        abort("Call *_env before this task.")

    from time import time
    env.current_release = "%(releases_path)s/%(time).0f" % { 'releases_path':env.releases_path, 'time':time() }

    run("mkdir -p %(target_dir)s" % { 'target_dir':env.current_release })
    for p in env.packages:
        put(p, env.current_release)

@roles('web')
def web_stop():
    if not env.has_key('shared_path'):
        execute(web_env)
    run("kill `cat %(shared_dir)s/RUNNING_PID`" % {"shared_dir":env.shared_path}, shell=False)

@roles('web')
def web_start():
    run("shared/bin/projectfoo-website -Dconfig.file=shared/conf/application-production.conf > /dev/null 2>&1 &", pty=False)

@roles('web')
def web_restart():
    execute(web_stop)
    execute(web_start)

@roles('web')
def web_deploy():
    execute(web_env)
    execute(web_setup)
    execute(common_deploy)
    execute(common_symlink)
    execute(common_cleanup)
    execute(web_restart)

def deploy():
    execute(batch_deploy)
    execute(web_deploy)

def common_rollback_code():
    if not env.has_key('releases'):
        execute(common_releases)
    if len(env.releases) >= 2:
        env.current_revision = env.releases[-1]
        env.previous_revision = env.releases[-2]
        env.current_release = "%(releases_path)s/%(current_revision)s" % { 'releases_path':env.releases_path, 'current_revision':env.current_revision }
        env.previous_release = "%(releases_path)s/%(previous_revision)s" % { 'releases_path':env.releases_path, 'previous_revision':env.previous_revision }
        run("rm %(current_path)s; ln -s %(previous_release)s %(current_path)s && rm -rf %(current_release)s" % { 'current_release':env.current_release, 'previous_release':env.previous_release, 'current_path':env.current_path })

@roles('web')
def web_rollback():
    execute(web_env)
    execute(web_setup)
    execute(common_rollback_code)
    execute(web_restart)

@roles('batch')
def batch_rollback():
    execute(batch_env)
    execute(batch_setup)
    execute(common_rollback_code)