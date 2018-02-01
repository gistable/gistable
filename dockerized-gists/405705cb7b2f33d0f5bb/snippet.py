# to install xplenty python SDK run: pip install xplenty
# more info here: https://github.com/xplenty/xplenty.py

from xplenty import XplentyClient
import time


account_id = ""  # your account id (http://app.xplenty.com/account_id/)
api_key = ""  # your api key (get it here https://app.xplenty.com/settings/edit)
cluster_nodes = 1  # required number of nodes in cluster

client = XplentyClient(account_id, api_key)

"""
# workflow overview

The workflow is comprised of steps which are run serially.
Each step contains one or more packages that are run in parallel.
All packages in a step must finish successfully in order for the workflow to continue to the next step.
The code below creates a cluster and starts running the workflow, one step at a time.
If a package fails, execution is stopped. No more jobs are executed and the cluster is terminated.

# workflow syntax

workflow = [
            [{"id": package_id, "name": "your descriptive name", "variables": {"var_name": "expression(...)"}}]  # this is step 1, it contains one package
            ,[{"id:package_id, "name":"step2pkg1","variables":{}}, {"id:package_id, "name":"step2pkg2","variables":{}} ]  # this is step2, it contains two packages
            ]

# workflow example
workflow = [
    [{"id": 12345, "name": "pkg 1", "variables": {"a": "UPPER('abc')"}}, {"id": 12344, "name": "pkg 2", "variables": {"a": "UPPER('def')"}}],
    [{"id": 12444, "name": "pkg 3", "variables": {"a": "UPPER('ghi')"}}],
    ]
"""

workflow = []


def GetExistingCluster():
    clusters = client.clusters
    for cluster in clusters:
        if cluster.status in ['available', 'creating'] and cluster.nodes == cluster_nodes:
            print '\nfound matching cluster\n\n'
            return cluster
    return None


def CreateCluster():
        print 'Creating cluster'
        return client.create_cluster('distributed', cluster_nodes, None, None, True, 600)


def RunFlow(cl):
    for step in workflow:
        for package in step:  # start jobs in step
            package['job'] = client.add_job(cl.id, package['id'], dynamic_vars=package['variables'])  # run a job and store its details in the package obj
            print 'Started job {1} for package {0}'.format(package['name'], package['job'].id)
        while True:           # poll job statuses
            AllJobsInStepsCompleted = True
            print "polling job statuses..."
            for package in step:  # poll job statuses
                if package['job'].status != 'completed':
                    package['job'].status = client.get_job(package['job'].id).status
                    AllJobsInStepsCompleted = False
                if package['job'].status in ['failed', 'stopped']:
                    print 'job {0} failed, stopping workflow'.format(package['job'].id)
                    return False  # failure
            if AllJobsInStepsCompleted:
                break
            time.sleep(30)
    return True  # success


def main():
    if account_id == "":
        print "account_id required"
        return
    if api_key == "":
        print "api_key required"
        return
#  get existing cluster or create
    cl = GetExistingCluster()
    if cl is None:  # create cluster
        cl = CreateCluster()
    RunFlow(cl)                           # run flow on cluster
    cl = client.terminate_cluster(cl.id)  # terminate cluster


if __name__ == '__main__':
    main()
