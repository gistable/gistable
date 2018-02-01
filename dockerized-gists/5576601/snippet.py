def upload_tar():
    # First, get the last deployed commit's short hash. 1st time, just create the file manually.
    last_deployed = local('cat last_deployed', capture=True)
    # get the last commit's short hash
    current_commit = local('git rev-parse --short HEAD', capture=True)
    # get the list of changed files since last deployed commit, put them in a tgz file, named as the commit to be deployed.
    local('git archive --format tar HEAD $(git diff --name-only HEAD %s) | gzip -9 > %s.tgz' % (last_deployed, current_commit))
    # put the .tgz file to server, in project's archive/ directory
    put('%s.tgz' % current_commit, '%s/archive/' % env.path)
    # move the local file inside the archive/ directory, so the root is clean
    local('mv %s.tgz archive/' % current_commit)
    # go inside the project directory on server
    with cd(env.path):
        # extract the files, they'll be overwritten
        run('tar -zxvf archive/%s.tgz' % current_commit)
        # finally, save the deployed commit's short hash in last_deployed file
        local('echo "%s" > last_deployed' % current_commit)