import os
import subprocess
import argparse

import requests


def changed_files(workdir, prevcommit, commit, cmd='git'):
    p = subprocess.Popen([cmd, 'diff', '--name-only', prevcommit, commit], 
            cwd=workdir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout,stderr = p.communicate()
    return stdout.splitlines()

def get_apiurl(buildurl):
    return os.path.join(buildurl, 'api/json')

def get_build_data(buildurl):
    apiurl = get_apiurl(buildurl)
    return requests.get(apiurl).json()

def find_last_built_revision(data):
    for action in data['actions']:
        last_built = action.get('lastBuiltRevision')
        if last_built is not None:
            return last_built['SHA1']
    

class JenkinsBuild(object):
    def __init__(self, buildurl):
        self.url = buildurl
        self.number = None
        self.commit = None
        if buildurl:
            data = get_build_data(buildurl)
            self.number = data['number']
            self.commit = find_last_built_revision(data)


def get_last_successful_build(joburl):
    jobdata = get_build_data(joburl)
    return JenkinsBuild(jobdata['lastSuccessfulBuild']['url'])

if __name__ == '__main__':
    workspace =     os.environ.get('WORKSPACE')
    commit =        os.environ.get('GIT_COMMIT')
    prevcommit =    os.environ.get('GIT_PREVIOUS_COMMIT')
    joburl =        os.environ.get('JOB_URL')

    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace',  required=workspace is None, default=workspace)
    parser.add_argument('--joburl',     required=joburl is None,    default=joburl)
    parser.add_argument('--commit',     required=commit is None,    default=commit)
    parser.add_argument('--prevcommit',                             default=prevcommit)                                                
    args = parser.parse_args()

    last_build = get_last_successful_build(args.joburl)
    print('Current Revision: ' + args.commit)
    print('Previous Revision: ' + last_build.commit)
    print('Previous Build Url: ' + last_build.url)
    print('========== CHANGES ============')
    for x in changed_files(args.workspace, last_build.commit, args.commit):
        print(x)

    #print('========== ENVIRON ============')
    #for k,v in sorted(((k,v) for k,v in os.environ.iteritems()), key=lambda x: x[0].lower()):
    #    print('%s : %s' % (k,v))
