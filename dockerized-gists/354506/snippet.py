from fabric.api import env, run, sudo, local, put

def production():
    """Defines production environment"""
    env.user = "deploy"
    env.hosts = ['example.com',]
    env.base_dir = "/var/www"
    env.app_name = "app"
    env.domain_name = "app.example.com"
    env.domain_path = "%(base_dir)s/%(domain_name)s" % { 'base_dir':env.base_dir, 'domain_name':env.domain_name }
    env.current_path = "%(domain_path)s/current" % { 'domain_path':env.domain_path }
    env.releases_path = "%(domain_path)s/releases" % { 'domain_path':env.domain_path }
    env.shared_path = "%(domain_path)s/shared" % { 'domain_path':env.domain_path }
    env.git_clone = "git@github.com:example/app.git"
    env.env_file = "deploy/production.txt"

def releases():
    """List a releases made"""
    env.releases = sorted(run('ls -x %(releases_path)s' % { 'releases_path':env.releases_path }).split())
    if len(env.releases) >= 1:
        env.current_revision = env.releases[-1]
        env.current_release = "%(releases_path)s/%(current_revision)s" % { 'releases_path':env.releases_path, 'current_revision':env.current_revision }
    if len(env.releases) > 1:
        env.previous_revision = env.releases[-2]
        env.previous_release = "%(releases_path)s/%(previous_revision)s" % { 'releases_path':env.releases_path, 'previous_revision':env.previous_revision }

def start():
    """Start the application servers"""
    sudo("/etc/init.d/apache2 start")

def restart():
    """Restarts your application"""
    sudo("/etc/init.d/apache2 force-reload")

def stop():
    """Stop the application servers"""
    sudo("/etc/init.d/apache2 stop")

def permissions():
    """Make the release group-writable"""
    sudo("chmod -R g+w %(domain_path)s" % { 'domain_path':env.domain_path })
    sudo("chown -R www-data:www-data %(domain_path)s" % { 'domain_path':env.domain_path })

def setup():
    """Prepares one or more servers for deployment"""
    run("mkdir -p %(domain_path)s/{releases,shared}" % { 'domain_path':env.domain_path })
    run("mkdir -p %(shared_path)s/{system,log,index}" % { 'shared_path':env.shared_path })
    permissions()

def checkout():
    """Checkout code to the remote servers"""
    from time import time
    env.current_release = "%(releases_path)s/%(time).0f" % { 'releases_path':env.releases_path, 'time':time() }
    run("cd %(releases_path)s; git clone -q -o deploy --depth 1 %(git_clone)s %(current_release)s" % { 'releases_path':env.releases_path, 'git_clone':env.git_clone, 'current_release':env.current_release })

def update():
    """Copies your project and updates environment and symlink"""
    update_code()
    update_env()
    symlink()
    permissions()

def update_code():
    """Copies your project to the remote servers"""
    checkout()
    permissions()

def symlink():
    """Updates the symlink to the most recently deployed version"""
    if not env.has_key('current_release'):
        releases()
    run("ln -nfs %(current_release)s %(current_path)s" % { 'current_release':env.current_release, 'current_path':env.current_path })
    run("ln -nfs %(shared_path)s/log %(current_release)s/log" % { 'shared_path':env.shared_path, 'current_release':env.current_release })
    run("ln -nfs %(shared_path)s/index %(current_release)s/index" % { 'shared_path':env.shared_path, 'current_release':env.current_release })
    run("ln -nfs %(shared_path)s/cdlm.db %(current_release)s/cdlm.db" % { 'shared_path':env.shared_path, 'current_release':env.current_release })
    run("ln -nfs %(shared_path)s/system/local.py %(current_release)s/%(app_name)s/local.py" % { 'shared_path':env.shared_path, 'current_release':env.current_release, 'app_name':env.app_name })
    run("ln -nfs %(current_release)s/env/src/django/django/contrib/admin/media %(current_release)s/%(app_name)s/media/admin" % { 'current_release':env.current_release, 'app_name':env.app_name })

def update_env():
    """Update servers environment on the remote servers"""
    if not env.has_key('current_release'):
        releases()
    run("cd %(current_release)s; virtualenv --no-site-packages --unzip-setuptools env" % { 'current_release':env.current_release })
    run("pip -q install -E %(current_release)s/env -r %(current_release)s/%(env_file)s" % { 'current_release':env.current_release, 'env_file':env.env_file })
    permissions()

def migrate():
    """Run the migrate task"""
    if not env.has_key('current_release'):
        releases()
    run("source %(current_release)s/env/bin/activate; cd %(current_release)s; python %(app_name)s/manage.py migrate" % { 'current_release':env.current_release, 'app_name':env.app_name })

def migrations():
    """Deploy and run pending migrations"""
    update_code()
    update_env()
    migrate()
    symlink()
    restart()

def cleanup():
    """Clean up old releases"""
    if not env.has_key('releases'):
        releases()
    if len(env.releases) > 3:
        directories = env.releases
        directories.reverse()
        del directories[:3]
        env.directories = ' '.join([ "%(releases_path)s/%(release)s" % { 'releases_path':env.releases_path, 'release':release } for release in directories ])
        run("rm -rf %(directories)s" % { 'directories':env.directories })

def enable():
    """Makes the application web-accessible again"""
    run("rm %(shared_path)s/system/maintenance.html" % { 'shared_path':env.shared_path })

def disable(**kwargs):
    """Present a maintenance page to visitors"""
    import os, datetime
    from django.conf import settings
    try:
        settings.configure(
            DEBUG=False, TEMPLATE_DEBUG=False, 
            TEMPLATE_DIRS=(os.path.join(os.getcwd(), 'templates/'),)
        )
    except EnvironmentError:
        pass
    from django.template.loader import render_to_string
    env.deadline = kwargs.get('deadline', None)
    env.reason = kwargs.get('reason', None)
    open("maintenance.html", "w").write(
        render_to_string("maintenance.html", { 'now':datetime.datetime.now(), 'deadline':env.deadline, 'reason':env.reason }).encode('utf-8')
    )
    put('maintenance.html', '%(shared_path)s/system/maintenance.html' % { 'shared_path':env.shared_path })
    local("rm maintenance.html")

def rollback_code():
    """Rolls back to the previously deployed version"""
    if not env.has_key('releases'):
        releases()
    if len(env.releases) >= 2:
        env.current_release = env.releases[-1]
        env.previous_revision = env.releases[-2]
        env.current_release = "%(releases_path)s/%(current_revision)s" % { 'releases_path':env.releases_path, 'current_revision':env.current_revision }
        env.previous_release = "%(releases_path)s/%(previous_revision)s" % { 'releases_path':env.releases_path, 'previous_revision':env.previous_revision }
        run("rm %(current_path)s; ln -s %(previous_release)s %(current_path)s && rm -rf %(current_release)s" % { 'current_release':env.current_release, 'previous_release':env.previous_release, 'current_path':env.current_path })

def rollback():
    """Rolls back to a previous version and restarts"""
    rollback_code()
    restart()

def cold():
    """Deploys and starts a `cold' application"""
    update()
    migrate()
    start()

def deploy():
    """Deploys your project. This calls both `update' and `restart'"""
    update()
    restart()