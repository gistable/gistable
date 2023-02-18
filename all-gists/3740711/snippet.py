from fabric.api import env, local, require


def deploy():
    """fab [environment] deploy"""
    require('environment')
    maintenance_on()
    push()
    syncdb()
    migrate()
    maintenance_off()
    ps()


def maintenance_on():
    """fab [environment] maintenance_on"""
    require('environment')
    local('heroku maintenance:on --remote %s' % env.environment)


def maintenance_off():
    """fab [environment] maintenance_off"""
    require('environment')
    local('heroku maintenance:off --remote %s' % env.environment)


def push():
    """fab [environment] push"""
    require('environment')
    local('git push %s main' % env.environment)


def syncdb():
    """fab [environment] syncdb"""
    require('environment')
    if(env.environment == "development"):
        local('foreman run python manage.py syncdb')
    else:
        local('heroku run python manage.py syncdb --remote %s' % env.environment)


def migrate(app=None):
    """fab [environment] migrate"""
    require('environment')
    if(env.environment == "development"):
        if(app is not None):
            local('foreman run python manage.py migrate %s' % app)
        else:
            local('foreman run python manage.py migrate')
    else:
        if(app is not None):
            local('heroku run python manage.py migrate %s --remote %s' % (app, env.environment))
        else:
            local('heroku run python manage.py migrate --remote %s' % env.environment)


def schemamigration(app):
    """fab schemamigration:[app]"""
    local('foreman run "python manage.py schemamigration %s --auto"' % app)


def ps():
    """fab [environment] ps"""
    require('environment')
    local('heroku ps --remote %s' % env.environment)


def open():
    """fab [environment] open"""
    require('environment')
    local('heroku open --remote %s' % env.environment)


def development():
    """fab development [command]"""
    env.environment = 'development'


def staging():
    """fab staging [command]"""
    env.environment = 'staging'


def production():
    """fab production [command]"""
    env.environment = 'production'
