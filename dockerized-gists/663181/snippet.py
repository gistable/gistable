
from __future__ import with_statement

import functools
import os
import sys
from fabric.api import *
from fabric.colors import green, red, green
import datetime
import re

#Some environment information to customize
APPENGINE_DEV_APPSERVER = "/usr/local/bin/dev_appserver.py"
APPENGINE_PATH = "/usr/local/google_appengine/"
APPENGINE_APP_CFG = "/usr/local/bin/appcfg.py"
PYTHON = "/opt/local/bin/python2.5"

#default values
env.version = "staging"
env.gae_email = "jeremi23@gmail.com"
env.gae_src = "src/"

def fix_appengine_path():
    EXTRA_PATHS = [
      APPENGINE_PATH,
      os.path.join(APPENGINE_PATH, 'lib', 'antlr3'),
      os.path.join(APPENGINE_PATH, 'lib', 'django'),
      os.path.join(APPENGINE_PATH, 'lib', 'fancy_urllib'),
      os.path.join(APPENGINE_PATH, 'lib', 'ipaddr'),
      os.path.join(APPENGINE_PATH, 'lib', 'webob'),
      os.path.join(APPENGINE_PATH, 'lib', 'yaml', 'lib'),
    ]
    
    sys.path = EXTRA_PATHS + sys.path

fix_appengine_path()
from google.appengine.api import appinfo

def include_appcfg(func):
    """Decorator that ensures the current Fabric env has a GAE app.yaml config
    attached to it."""
    @functools.wraps(func)
    def decorated_func(*args, **kwargs):
        if not hasattr(env, 'app'):
            appcfg = appinfo.LoadSingleAppInfo(open(env.gae_src + 'app.yaml'))
            env.app = appcfg
        return func(*args, **kwargs)
    return decorated_func

def last_tag():
    print(green("Last %s tag: %s" % (env.version, get_last_tag_match("%s-*" % env.version))))

def staging():
    """Sets the deployment target to staging."""
    #env.app.application = '%s-staging' % env.app.application
    env.version = "staging"
    pass

def production():
    """Sets the deployment target to production."""
    env.version = "production"
    
def version(version):
    env.version = version
    
def tgz():
    tag = get_last_tag_match("%s*" % env.version)
    local("git archive --format=tar %s | gzip > tag_%s.tar.gz" % (tag, tag))
    
@include_appcfg
def deploy(tag=None):
    if not is_working_directory_clean():
        abort("Working directory should be clean before deploying")
    
    prepare_deploy(tag)
    local('%s %s -A %s -V %s --email=%s update %s' % (PYTHON, APPENGINE_APP_CFG, env.app.application, env.app.version, env.gae_email, env.gae_src), capture=False)
    end_deploy()

def run():
    local("%s %s --port 8080  --use_sqlite %s" % (PYTHON, APPENGINE_DEV_APPSERVER, env.gae_src), capture=False)

def help():
    print("environments:")
    print("    staging")
    print("    production")
    print("    version")
    print("")
    print("command:")
    print("    run")
    print("    deploy")
    print("    last_tag")
    print("    tgz")

##############################
# helpers
##############################
def prepare_deploy(tag=None):
    print(green("Preparing the deployement to %s" % env.version))
    
    if env.version == "staging":
        env.app.version = env.version
        if tag != None:
            if tag.find("staging") != 0 or get_last_tag_match(tag) == None:
                abort("Can only deploy to staging a staging tag; use 'fab deploy:staging-YYYY-MM-DD.X'")
            env.deployement_tag = tag
        else:
            do_staging_tag()
    elif env.version == "production":     
        if tag != None:
            if tag.find("production") == 0 and get_last_tag_match(tag) != None:
                env.deployement_tag = tag
            else:
                do_production_tag(tag)
        else:
            abort("Staging tag required; use 'fab production deploy:staging-YYYY-MM-DD.X'")

    # Where are we checking out a clean copy?
    deploy_path = local('mktemp -d -t %s' % env.app.application)
    local('git clone . %s' % deploy_path)
    
    with cd(deploy_path):
        local('git checkout %s' % env.deployement_tag)
        #local('git submodule init')
        #local('git submodule update')
        local('find . -name ".git*" | xargs rm -rf')
        print(green('App: %s' % env.app.application))
        print(green('Ver: %s' % env.app.version))
    
    env.deploy_path = deploy_path

def end_deploy():
    print(green("Cleaning up after the deploy"))
    local('rm -r %s' % env.deploy_path)
    #update_tag("current_%s_version" % env.version, env.deployement_tag)

def check_if_last_version():
    branch = local("git branch --no-color 2> /dev/null | sed -e '/^[^*]/d'").replace("* ", "").strip()
    local_sha = local("git log --pretty=format:%H HEAD -1").strip()
    origin_sha = local("git log --pretty=format:%%H %s -1" % branch).strip()
    if local_sha != origin_sha:
        abort("""
        Your %s branch is not up to date with origin/%s.
        Please make sure you have pulled and pushed all code before deploying:

        git pull origin %s
        #run tests, etc
        git push origin %s

        """ % (branch, branch, branch, branch))

def get_last_tag_match(str):
    tags = local(" git tag -l '%s'" % str)
    if len(tags) == 0:
        return None
    tags = tags.split()
    tags.sort()
    return tags[-1]

def do_production_tag(tag_to_promote):
    if tag_to_promote.find("staging") != 0:
        abort("Staging tag required; use 'fab production deploy:staging-YYYY-MM-DD.X'")
    tag_to_promote = get_last_tag_match(tag_to_promote)
    if tag_to_promote == None:
        abort("Staging tag \"%s\" does not exist." % tag_to_promote)
    
    (last_tag_name, next_tag_name) = get_tags_name()

    if need_to_tag(tag_to_promote, last_tag_name):
        print(green("Tagging the last %s with %s" % (env.version, next_tag_name)))
        local("git tag -a -m 'tagging current code for deployment to %s' %s %s" % (env.version, next_tag_name, tag_to_promote))
        env.deployement_tag = next_tag_name
    else:
        env.deployement_tag = last_tag_name

def do_staging_tag():
    (last_tag_name, next_tag_name) = get_tags_name()

    if need_to_tag("HEAD", last_tag_name):
        local("git tag -a -m 'tagging current code for deployment to %s' %s" % (env.version, next_tag_name))
        env.deployement_tag = next_tag_name
    else:
        env.deployement_tag = last_tag_name

def update_tag(tag_name, from_tag):
    if get_last_tag_match(tag_name) != None:
        local("git tag -d %s" % tag_name)
    local("git tag -a -m 'updating %s to %s' %s %s" % (tag_name, from_tag, tag_name, from_tag))

def need_to_tag(version1, version2):
    sha_version1 = local("git log --pretty=format:%%H %s -1" % version1)
    if version2:
        sha_version2 = local("git log --pretty=format:%%H %s -1" % version2)
        if sha_version1 == sha_version2:
            print(green("No need to tag, the last %s tag is the same as the current version" % env.version))
            return False
    return True

def is_working_directory_clean():
    status = local("git status")
    if status.find("working directory clean") > -1:
        print(green("Working directory clean."))
        return True
    print(red("Working directory not clean."))
    return False


def get_tags_name():
    num = 1
    today = datetime.date.today()
    next_tag_name = "%s-%i-%.2i-%.2i" % (env.version, today.year, today.month, today.day)
    
    last_tag_name = get_last_tag_match(next_tag_name + ".*")
    if last_tag_name == None:
        num = 1
    else:
        match = re.search("%s-[0-9]{4}-[0-9]{2}-[0-9]{2}\.([0-9]*)" % env.version, last_tag_name)
        num = int(match.group(1)) + 1
    
    next_tag_name = "%s.%.3i" % (next_tag_name, num)
    print(green("Last tag name: %s" % last_tag_name))
    print(green("Next tag name: %s" % next_tag_name))
    return (last_tag_name, next_tag_name)
    
    
