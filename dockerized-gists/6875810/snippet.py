"""
Tasks for managing a test server
"""
import os
from fabric.api import cd, env, prefix, run, sudo, task
from fabric.contrib.files import exists, sed
from fabric.context_managers import hide
from fabric.colors import green, red


def _make_link_cmd(source, link):
    """
    Generates the command string to make a link (if it doesn't exist)
    """
    return "[ ! -L %s ] && ln -s %s %s" % (link, source, link)


def _process_template(source, instance_name):
    """
    Copy a template to a final destination and rename {branchname} to instance_name
    """
    if isinstance(source, (list, tuple)):
        source = os.path.join(*source)
    dest = source.replace('.template', '')
    if not exists(dest):
        run('cp %s %s' % (source, dest))
        sed(dest, '\\{branchname\\}', instance_name)
    return dest


def _bootstrap(tag, settings='production'):
    """
    Bootstrap a deployment. Sets up a virtualenv, runs bootstrap.py, collects
    the static files, and sets up the database.
    """
    deploy_dir = "%s%s" % (env.site_root, tag)
    virtualenv = "%s/virtualenv" % deploy_dir
    settings_file = settings
    if 'settings' not in settings:
        settings_file = 'settings.%s' % settings

    # Bootstrap the code
    with cd(deploy_dir):
        run("python bootstrap.py")
        with prefix('source %s/bin/activate' % virtualenv):
            run("./manage.py collectstatic --noinput --verbosity 0 --settings %s" % settings_file)
            run("./manage.py syncdb --settings %s" % settings_file)
            run("./manage.py migrate --delete-ghost-migrations --settings %s" % settings_file)


def _list_test_instances():
    with hide('running', 'stdout', 'stderr'):
        output = run('ls -1 %s' % env.site_root)
    instances = [x.strip() for x in output.split("\n")]
    return instances


@task
def make_test_instance(branchname, instance_name=""):
    """
    Make a stand-alone instance using branch <branchname>

    Named using <instance_name> or <branchname>
    """
    if not instance_name:
        instance_name = branchname
    instance_dir = env.site_root + instance_name
    if not exists(instance_dir):
        with cd(env.site_root):
            run('git clone %s %s' % (env.repo_url, instance_name))
        with cd(instance_dir):
            run('git checkout %s' % branchname)
    else:
        with cd(instance_dir):
            run("git pull")

    _process_template((instance_dir, 'settings', 'test.py.template'),
                      instance_name)
    run('mkdir -p %s' % os.path.join(instance_dir, 'staticmedia', 'CACHE'))
    sudo('chmod -R a+w %s' % os.path.join(instance_dir, 'staticmedia', 'CACHE'))
    _bootstrap(instance_name, 'test')
    sudo('chgrp -R www-data %s%s/staticmedia' % (env.site_root, instance_name))
    sudo('chmod -R g+w %s%s/staticmedia' % (env.site_root, instance_name))

    upstart_conf = _process_template((instance_dir, 'conf', 'upstart-test.conf.template'),
                      instance_name)
    upstart_link = "/etc/init/%s.conf" % instance_name
    sudo(_make_link_cmd(upstart_conf, upstart_link))
    sudo('initctl reload-configuration')

    web_conf = _process_template((instance_dir, 'conf', 'nginx-test.conf.template'),
                      instance_name)
    web_link = '/etc/nginx/sites-available/%s' % instance_name
    if not exists(web_link):
        sudo(_make_link_cmd(web_conf, web_link))
        sudo('nxensite %s' % instance_name)
    sudo('/etc/init.d/nginx reload')


@task
def remove_test_instance(instance_name):
    """
    Remove a test instance and remove all support scripts and configs
    """
    nginx_name = '/etc/nginx/sites-enabled/%s' % instance_name
    if exists(nginx_name):
        sudo('nxdissite %s' % instance_name)
        sudo('/etc/init.d/nginx reload')
    nginx_name = '/etc/nginx/sites-available/%s' % instance_name
    if exists(nginx_name):
        sudo('rm %s' % nginx_name)

    upstart_link = "/etc/init/%s.conf" % instance_name
    if exists(upstart_link):
        sudo('stop %s' % instance_name)
        sudo('rm %s' % upstart_link)
        sudo('initctl reload-configuration')

    instance_dir = env.site_root + instance_name
    if exists(instance_dir):
        sudo('rm -Rf %s' % instance_dir)


def _instance_mgmt(cmd, instance_name=None):
    """
    Executes <cmd> against <instance_name> or every instance
    """
    env.warn_only = True
    if instance_name is not None:
        instances = [instance_name]
    else:
        instances = _list_test_instances()
    for item in instances:
        sudo("%s %s" % (cmd, item.strip()))

@task
def stop_test_instance(instance_name=None):
    """
    Stop one or all the test instances
    """
    _instance_mgmt("stop", instance_name)


@task
def start_test_instance(instance_name=None):
    """
    Start one or all the test instances
    """
    _instance_mgmt("start", instance_name)


@task
def restart_test_instance(instance_name):
    """
    Restart one or all the test instances
    """
    _instance_mgmt("restart", instance_name)


@task
def list_test_instances():
    """
    List all the test instances on the test server
    """
    instances = _list_test_instances()
    output = ["", "Instance Name  Status", "-------------- -------------"]
    with hide('running', 'stdout'):
        for instance in instances:
            line = run('status %s' % instance)
            line = line.replace(",", "")
            line = line.split(" ")
            if len(line) == 2:
                output.append(red(line[0].ljust(15)) + line[1])
            elif len(line) == 4:
                output.append(green(line[0].ljust(15)) + line[1])
    print "\n".join(output)


@task
def update_test_instance(instance_name):
    """
    Update the <instance_name>
    """
    instance_dir = env.site_root + instance
    settings = "settings.test"
    with cd(instance_dir):
        run("git pull")

        with prefix('source virtualenv/bin/activate'):
            run("pip install -r requirements.txt")
            run("./manage.py collectstatic --noinput --verbosity 0 --settings %s" % settings)
            run("./manage.py syncdb --settings %s" % settings)
            run("./manage.py migrate --delete-ghost-migrations --settings %s" % settings)
            sudo("restart %s" % instance_name)
