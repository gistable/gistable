import os
import argparse
import json
from pprint import pprint
from tempfile import NamedTemporaryFile
from jinja2 import Environment, PackageLoader
from libcloud.common.types import ProviderError
from libcloud.compute.types import Provider
from libcloud.compute.deployment import (MultiStepDeployment,
    ScriptDeployment, ScriptFileDeployment, FileDeployment)
from libcloud.compute.providers import get_driver

#setup jinja environment
env = Environment(loader=PackageLoader('openwpm-deploy', 'templates'))


def deploy_wpm_master(driver, password):
    scopes = [
        {
            'email': 'default',
            'scopes': ['compute', 'storage-full']
        }
    ]
    # render the compose.yaml
    compose_yaml_template = env.get_template('master-compose.jinja.yml')
    compose_yaml = compose_yaml_template.render(password=password)
    deploy_template = env.get_template('deploy.jinja.sh')
    deploy = deploy_template.render(docker_compose=compose_yaml)

    with NamedTemporaryFile(delete=False) as f:
        f.write(deploy)
        name = f.name
    master = driver.deploy_node(name="master",
                                    size='g1-small',
                                    image='ubuntu-1404-trusty',
                                    script=name,
                                    location='us-central1-f',
                                    ex_service_accounts=scopes)
    return master


def deploy_wpm_analysis_worker(driver):
    scopes = [
        {
            'email': 'default',
            'scopes': ['compute', 'storage-full']
        }
    ]
    # render the compose.yaml
    compose_yaml_template = env.get_template('analysis-worker-compose.jinja.yml')
    compose_yaml = compose_yaml_template.render()
    deploy_template = env.get_template('deploy.jinja.sh')
    deploy = deploy_template.render(docker_compose=compose_yaml)

    with NamedTemporaryFile(delete=False) as f:
        f.write(deploy)
        name = f.name
    worker = driver.deploy_node(name="worker",
                                size='n1-standard-16',
                                image='ubuntu-1404-trusty',
                                script=name,
                                location='us-central1-f',
                                ex_service_accounts=scopes)
    return worker


def setup_wpm_network(driver):
    driver.ex_create_firewall('ipython-notebook', [{'IPProtocol': 'tcp',
                                                    'ports': [8888]}])
    driver.ex_create_firewall('spark-web-ui', [{'IPProtocol': 'tcp',
                                                'ports': [8080]}])


def deploy_wpm(project_id, pem_uri, service_account_email, password):
    # Connect to GCE
    driver = get_driver(Provider.GCE)(service_account_email,
                                      pem_uri,
                                      project=project_id)
    try:
        setup_wpm_network(driver)
    except ProviderError:
        net = None
        print "Error when setting up network"
    try:
        master = deploy_wpm_master(driver, password)
    except ProviderError:
        master = None
        print "Error when setting up master"
    try:
        worker = deploy_wpm_analysis_worker(driver)
    except ProviderError:
        print "Error when setting up worker"
        worker = None
    return {'master': master, 'worker': worker}


def wait_for_master(url, retry_count=10):
    import urllib2
    print "Waiting for {0}".format(url)
    count = 1
    while True:
        print "Attempt {0}".format(count)
        try:
            urllib2.urlopen("https://{0}:8888".format(url))
            break
        except urllib2.URLError:
            count += 1
            continue


def main():
    parser = argparse.ArgumentParser(description='Deploy OpenWPM infrastructure')
    parser.add_argument('project_id', type=str, help='the project_id to deploy under')
    parser.add_argument('service_json', type=str, help='json file for service account')
    parser.add_argument('password', type=str, help='password for login')
    args = parser.parse_args()
    # load the service account email from the json file
    with open(args.service_json) as f:
        email = json.loads(f.read())['client_email']
    # ready aim fire
    ret = deploy_wpm(args.project_id, args.service_json, email, args.password)
    wait_for_master(ret['master'].public_ips[0])
    print "Master Notebook: https://{0}:8888".format(ret['master'].public_ips[0])

if __name__ == "__main__":
    main()