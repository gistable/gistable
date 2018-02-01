#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Get all your bitbucket issues at once-Fetches/Displays your bitbucket issues
-                                                                              
:copyright: (c) 2011 by Openlabs Technologies & Consulting (P) Limited         
:license: BSD, see LICENSE for more details.                                   
-                                                                              
The username and password for this program can be set in multiple ways.        
-                                                                              
1. Set environment variable                                                    
    Example:                                                                   
      export BBUSERNAME = <username>                                           
      export BBPASSWORD = <password>                                           
      export BBOWNER = <owner>                                                 
 -                                                                             
2. Create a file called .bitbucket in your home directory and set the following
-                                                                              
       [auth]                                                                  
       username = <username>                                                   
       passwrod = <password>                                                   
       owner = <owner>                                                         
-                                                                              
3. Pass as command line arguments when calling this program                    
-                                                                              
The concept of owner: In bitbucket the repositories are owned by an user while 
you may have been given access to it. So if you need issues on projects hosted 
by some other user as well, then you need to specify owner. If not by default  
the issues in projects owned by you are given                                  
"""
import urllib2
import urllib
import os
import ConfigParser
try:
    import simplejson as json
except ImportError:
    import json


class CommandDict(dict):
    """An implementation of dictionary which adds commands to dictioanry by the
    use of decorators
    """
    def add(self, func):
        self[func.__name__] = func


USERNAME = PASSWORD = OWNER = None
ALLOWED_COMMANDS = CommandDict()



class BitBucket(object):
    """Main bitbucket class.  Use an instantiated version of this class
    to make calls against the REST API."""

    base_url = 'https://api.bitbucket.org/1.0/'

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def call(self, url, data=None, as_json=True):
        auth = '%s:%s' % (self.username, self.password)
        auth = {'Authorization': 'Basic %s' % (auth.encode('base64').strip())}
        data = urllib.urlencode(data) if data else None
        request = urllib2.Request(self.base_url + url, data, auth)
        response = urllib2.urlopen(request).read()
        return (json.loads(response) if as_json else response)

    def get_repositories(self, user):
        "Return repositories owned by an user"
        return self.call('users/%s/' % user)['repositories']

    def get_issues(self, repository, search=None, filter=None, user=None):
        """Returns issues in a given repository"""
        user = user if user else self.username
        url = 'repositories/%s/%s/issues/' % (user, repository)
        if filter:
            url = "%s?%s" % (url, urllib.urlencode(filter))
        return self.call(url)

def set_authentication():
    """Extracts authentication according to above schema

    The auth through arguments when starting the program need not be handled 
    here since, the USERNAME and PASSWORD will be set automatically
    """
    if 'BBUSERNAME' in os.environ and 'BBPASSWORD' in os.environ:
        (USERNAME, PASSWORD, OWNER) = (os.environ['BBUSERNAME'], 
            os.environ['BBPASSWORD'], os.environ['BBOWNER'])
        return

    config_file = os.path.join(os.environ['HOME'], '.bitbucket')
    if os.path.exists(config_file):
        config = ConfigParser.RawConfigParser()
        config.read(config_file)
        USERNAME = config.get('auth', 'username')
        PASSWORD = config.get('auth', 'password')
        OWNER = config.get('auth', 'owner')

    raise Exception("No username and password given")

def get_authenticated_api():
    """Returns authenticated bit bucket API for the current user"""
    if USERNAME is None or PASSWORD is None:
        set_authentication()
    return BitBucket(USERNAME, PASSWORD)

def get_repositories(user):
    """Return list of slugs of user's repositries"""
    return [repo['slug'] for repo in user.repositories()]

@ALLOWED_COMMANDS.add
def my_issues(project=None, status='new'):
    """Displays all the issues assigned to you in a specific project if project
    is specified, else shows issues in all projects.

    :param project: slug of the project
    """
    api = get_authenticated_api()
    repository_names = [project] if project \
        else [r['slug'] for r in api.get_repositories(OWNER or USERNAME)]

    issue_count = 0
    for repository in repository_names:
        issues = api.get_issues(repository, filter={
            'status': status, 'responsible': USERNAME,
            },
            user=OWNER)

        if IGNORE_EMPTY and issues['count'] == 0:
            continue

        print "=" * 100
        print "Repository: %s Issue Count: %d" % (
            repository, issues['count'])
        print "-" * 100
        for issue in issues['issues']:
            uri = 'https://bitbucket.org/%s/issue/%s' 
            uri = uri % (
                '/'.join(issue['resource_uri'].split('/')[3:5]), 
                issue['local_id'])
            print "# %s: %s (%s)" % (
                issue['local_id'], issue['title'], uri)
        print "=" * 100

def execute_commands(commands):
    """Commands can be passed positional arguments using :
    For example

    bitbucket -u username -p password show_my_issues:projectx
    """
    for command in commands:
        if ':' in command:
            method_name, args = command.split(':', 1)
            pargs, kwargs = [], {}
            for arg in args.split(','):
                if '=' not in arg:
                    pargs.append(arg)
                else:
                    kwargs.update([arg.split('=')])
            ALLOWED_COMMANDS[method_name](*pargs, **kwargs)
        else:
            ALLOWED_COMMANDS[command]()


if __name__ == '__main__':
    from optparse import OptionParser
    usage = "usage: %prog [options] command"
    parser = OptionParser(usage=usage, description=__doc__)
    parser.add_option('-u', '--username', dest='username', default=None)
    parser.add_option('-p', '--password', dest='password', default=None)
    parser.add_option('-o', '--owner', dest='owner', default=None)
    parser.add_option('-i', '--ignore_empty', action="store_true", 
        dest='ignore_empty', default=False, help="""If you do not want to print 
the logs for projects which dont have issues or have zero number of 
issues, this can be set. Equivalent to setting -i when calling the program""")
    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.error("No command specified")

    USERNAME, PASSWORD, OWNER = options.username, options.password, options.owner
    IGNORE_EMPTY = options.ignore_empty

    execute_commands(args)
