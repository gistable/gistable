from fabric.api import run, local, task


@task(alias='hd')
def heroku_deploy(scale='yes', runtime='no', runtime_version=None):
    """
    Deploys heroku app

    Usage examples:

        fab heroku_deploy
        fab hd:runtime=yes
        fab hd:yes,yes,2.7.3

    :param scale: If set to 'no' heroku won't scale a web process after deployment
    :param runtime: If set to 'yes' heroku runtime will be toggled before deployment
    :param runtime_version: (optional) Runtime version for heroku_runtime() (ex: 2.7.3)
    :return:
    """
    if runtime == 'yes':
        heroku_runtime(version=runtime_version)
    local('git push heroku master')
    if scale == 'yes':
        local('heroku ps:scale web=1')


@task(alias='hr')
def heroku_runtime(version=None, commit='yes'):
    """
    Sets heroku python runtime

    Usage examples:

        fab heroku_runtime:2.7.2
        fab hr:2.7.3
        fab hr
        fab hr:commit=no

    :param version: Runtime version (ex: 2.7.3)
    :param commit: If set to 'no' git won't commit runtime.txt
    :return:
    """
    if not version:
        try:
            fd = open('runtime.txt', 'r')
            runtime = fd.read().strip()
            print 'runtime.txt says:', runtime
            runtime = 'python-2.7.2' if runtime.endswith('.3') else 'python-2.7.3'
        except IOError:
            runtime = 'python-2.7.2'
            print 'runtime.txt doesn\'t exist.'
    else:
        runtime = 'python-%s' % version
    print 'Setting runtime:', runtime
    local('echo "%s" > runtime.txt' % runtime)
    local('cat runtime.txt')
    if commit == 'yes':
        local('git commit runtime.txt -m "Changed heroku runtime to %s"' % runtime)


@task(alias='hc')
def heroku_clean(mode='enable', app=None):
    """
    Enables CLEAN_VIRTUALENV for heroku deployment

    http://stackoverflow.com/questions/8937905/how-to-pip-uninstall-with-virtualenv-on-heroku-cedar-stack/9463068

    Usage examples:

        fab hc
        fab heroku_clean
        fab hc:app=myapp
        fab hc:disable
        fab hc:disable,myapp

    :param mode: (optional) if set to 'disabled' it will overturn this configuration
    :param app: (optional) specifies a heroku app
    :return:
    """
    a = '-a %s' % app if app else ''
    config_mode = 'add' if mode == 'enable' else 'remove'
    repo = 'blaze33' if mode == 'enable' else 'heroku'
    local('heroku labs:%s user-env-compile %s' % (mode, a))
    local('heroku config:add BUILDPACK_URL=git://github.com/%s/heroku-buildpack-python.git' % repo)
    local('heroku config:%s CLEAN_VIRTUALENV=true' % config_mode)