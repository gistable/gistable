import os
from fabric.api import env, run, prompt, local, get
from fabric.state import output

env.environment = ""
env.hosts = ["example.com"]
env.user = "admin"
env.full = False

output['running'] = False

def dev():
    """ chooses development environment """
    env.environment = "dev"
    print("LOCAL DEVELOPMENT ENVIRONMENT\n")

def staging():
    """ chooses testing environment """
    env.environment = "staging"
    print("STAGING WEBSITE\n")

def production():
    """ chooses production environment """
    env.environment = "production"
    print("PRODUCTION WEBSITE\n")

def full():
    """ all commands should be executed without questioning """
    env.full = True

def _update_dev():
    """ updates development environment """
    run("") # password request
    print
    
    if env.full or "y" == prompt('Get latest production database (y/n)?', default="y"):
        print(" * creating production-database dump...")
        run('cd /path/to/database_backups && ./backup_database.bsh --latest')
        print(" * downloading dump...")
        get("/path/to/database_backups/db_latest.sql",
            "db_latest.sql")
        print(" * importing the dump locally...")
        local('cd /path/to/project '
            '&& python manage.py dbshell < /path/to/scripts/db_latest.sql '
            '&& rm scripts/db_latest.sql')
        print(" * removing production-database dump...")
        run('rm /path/to/database_backups/db_latest.sql')
        print
        if env.full or "y" == prompt('Call prepare_dev command (y/n)?', default="y"):
            print(" * preparing data for development...")
            local('cd /path/to/project '
                '&& python manage.py prepare_dev')
    print
        
    if env.full or "y" == prompt('Download media uploads (y/n)?', default="y"):
        print(" * creating an archive of media uploads...")
        run('cd /path/to/media/uploads '
            '&& tar -cz --exclude=.svn -f /path/to/tmp/uploads.tar.gz *')
        print(" * downloading archive...")
        get("/path/to/tmp/uploads.tar.gz",
            "uploads.tar.gz")
        print(" * extracting and removing archive locally...")
        for host in env.hosts:
            local('cd /path/to/media/uploads/ '
                '&& tar -xzf /path/to/scripts/uploads.tar.gz '
                '&& rm /path/to/scripts/uploads.tar.gz')
        print(" * removing archive from the server...")
        run("rm /path/to/tmp/uploads.tar.gz")
    print
    
    if env.full or "y" == prompt('Update code (y/n)?', default="y"):
        print(" * updating code...")
        local('cd /path/to/project && svn up')
    print
        
    if env.full or "y" == prompt('Migrate database schema (y/n)?', default="y"):
        print(" * migrating database schema...")
        local("cd /path/to/project && python manage.py migrate --no-initial-data")
        local("cd /path/to/project && python manage.py syncdb")
    print


def _update_staging():
    """ updates testing environment """
    run("") # password request
    print
    
    if env.full or "y" == prompt('Set under-construction screen (y/n)?', default="y"):
        print(" * changing httpd.conf and restarting apache")
        run('cd /path/to/apache/conf/ '
            '&& cp httpd_under_construction.txt httpd.conf '
            '&& /path/to/apache/bin/restart')
    print

    if env.full or "y" == prompt('Get latest production database (y/n)?', default="y"):
        print(" * updating database with production data...")
        run('cd /path/to/production/database_backups '
            '&& ./backupdb.bsh --latest '
            '&& cd /path/to/staging/project '
            '&& source /path/to/staging/bin/activate.bsh '
            '&& python manage.py dbshell < /path/to/production/database_backups/db_latest.sql')
        print
        if env.full or "y" == prompt('Call prepare_staging command (y/n)?', default="y"):
            print(" * preparing data for testing...")
            run('cd /path/to/staging/project '
                '&& source /path/to/staging/bin/activate.bsh '
                '&& python manage.py prepare_staging')
    print
    
    if env.full or "y" == prompt('Get latest media uploads (y/n)?', default="y"):
        print(" * updating media uploads...")
        run('/path/to/staging/scripts/get_latest_uploads.bsh')
    print
    
    if env.full or "y" == prompt('Update code (y/n)?', default="y"):
        print(" * updating code...")
        run('cd /path/to/staging/project '
            '&& svn up')
    print
    
    if env.full or "y" == prompt('Migrate database schema (y/n)?', default="y"):
        print(" * migrating database schema...")
        run('cd /path/to/staging/project '
            '&& source /path/to/staging/bin/activate.bsh '
            '&& python manage.py migrate --no-initial-data')
        run('cd /path/to/staging/project '
            '&& source /path/to/staging/bin/activate.bsh '
            '&& python manage.py syncdb')
    print
    
    if env.full or "y" == prompt('Unset under-construction screen (y/n)?', default="y"):
        print(" * changing httpd.conf and restarting apache")
        run('cd /path/to/staging/apache/conf/ '
            '&& cp httpd_live.txt httpd.conf '
            '&& /path/to/staging/apache/bin/restart')
    print

def _update_production():
    """ updates production environment """
    if "y" != prompt('Are you sure you want to update production website (y/n)?', default="n"):
        return
        
    run("") # password request
    print
    
    if env.full or "y" == prompt('Set under-construction screen (y/n)?', default="y"):
        print(" * changing httpd.conf and restarting apache")
        run('cd /path/to/production/apache/conf/ '
            '&& cp httpd_under_construction.txt httpd.conf '
            '&& /path/to/production/apache/bin/restart')
    print

    if env.full or "y" == prompt('Backup database (y/n)?', default="y"):
        print(" * creating a database dump...")
        run('cd /path/to/production/database_backups/ ' 
            '&& ./backupdb.bsh')
    print

    if env.full or "y" == prompt('Update code (y/n)?', default="y"):
        print(" * updating code...")
        run('cd /path/to/production/project '
            '&& svn up')
    print
    
    if env.full or "y" == prompt('Migrate database schema (y/n)?', default="y"):
        print(" * migrating database schema...")
        run('cd /path/to/production/project/ '
            '&& source /path/to/production/bin/activate.bsh '
            '&& python manage.py migrate --no-initial-data')
        run('cd /path/to/production/project/ '
            '&& source /path/to/production/bin/activate.bsh '
            '&& python manage.py syncdb')
    print

    if env.full or "y" == prompt('Unset under-construction screen (y/n)?', default="y"):
        print(" * changing httpd.conf and restarting apache")
        run('cd /path/to/production/apache/conf/ '
            '&& cp httpd_live.txt httpd.conf '
            '&& /path/to/production/apache/bin/restart')
    print


def deploy():
    """ updates the chosen environment """
    if not env.environment:
        while env.environment not in ("dev", "staging", "production"):
            env.environment = prompt('Please specify target environment ("dev", "staging", or "production"): ')
            print

    globals()["_update_%s" % env.environment]()
