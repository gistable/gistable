    #!/usr/bin/env python
    # post-receive hook for git-based deployments
    # https://edmondburnett.com/post/python-push-to-deploy

    import sys
    import os
    from subprocess import call

    # configuration
    deploy_to_path = '/path/to/deploy/directory/'
    deploy_branch  = 'main'

    def post_receive(from_commit, to_commit, branch_name):
        # Don't deploy if pushed branch != deploy_branch
        if not branch_name.endswith(deploy_branch):
            print('Received branch ' + branch_name + ', not deploying.')
            sys.exit()

        # copy files to deploy directory
        call('GIT_WORK_TREE="' + deploy_to_path + '" git checkout -f ' + branch_name, shell=True)
        print('DEPLOY: ' + branch_name + '(' + to_commit + ') copied to ' + deploy_to_path)

        # TODO: Deployment Tasks
        # i.e. Run a script, restart daemons, etc


    if __name__ == '__main__':
        # get values from STDIN
        fc,tc,bn = sys.stdin.read().split()
        post_receive(fc, tc, bn)