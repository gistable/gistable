#!/usr/bin/python

"""
Script to migrate marathon tasks from the host going for maintenance

optional arguments:
  -h, --help     show this help message and exit
  --url URL      Marathon URL (http://marathon.example.com)
  --hosts HOSTS  Hosts going to go for maintenance

Example Usage:
$ python marathon_cluster_maintenance.py --url http://marathon.example.com --hosts 172.31.37.92,172.31.35.101
"""

import sys
import json
import time
import argparse
import requests

apps_endpoint = "/v2/apps"
tasks_endpoint = "/v2/tasks"
deployment_endpoint = "/v2/deployments"

def parse_args():
  """ Parses command line arguments. """
  parser = argparse.ArgumentParser(description='Mesos Migration Script')
  parser.add_argument('--url', dest='url', type=str, help='Marathon URL (http://marathon.example.com)')
  parser.add_argument('--hosts', dest='hosts', type=str, help='Hosts going to go for maintenance')
  args = parser.parse_args()
  return args

def get_marathon_apps(marathon_endpoint):
  """
  Returns a dictionary of marathon-apps as key and
  their running instances count as value.
  """
  list_apps_url = marathon_endpoint + apps_endpoint
  running_instances = {}
  try:
    response = requests.get(list_apps_url)
    if response.status_code == 200:
      app_list = response.json()['apps']
      for app in app_list:
        running_instances[app['id']] = app['tasksRunning']
  except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(1)
  return running_instances

def get_marathon_tasks(marathon_endpoint, host):
  """
  Returns a dictionary of marathon-apps as key and
  their running instances count as value (for a host).
  """
  list_tasks_url = marathon_endpoint + tasks_endpoint
  running_tasks = {}
  try:
    response = requests.get(list_tasks_url)
    if response.status_code == 200:
      task_list = response.json()['tasks']
      for task in task_list:
        appId = task['appId']
        if task['host'] == host:
          if appId not in running_tasks.keys():
            running_tasks[appId] = 1
          else:
            running_tasks[appId] += 1
  except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(1)
  return running_tasks

def wait_for_deployment(marathon_endpoint, deploymentId):
  """
  Wait for the deployment to finish
  """
  deployment_url = marathon_endpoint + deployment_endpoint
  while True:
    deploymentIds = []
    try:
      response = requests.get(deployment_url)
      deployments = response.json()
      for deploy in deployments:
        deploymentIds.append(deploy['id'])
    except requests.exceptions.RequestException as e:
      print(e)
      sys.exit(1)
    if deploymentId in deploymentIds:
      print('Deployment %s is going on.' % deploymentId)
      time.sleep(10)
      continue
    else:
      print('Deployment %s has finished.' % deploymentId)
      return

def redeploy_with_constraints(marathon_endpoint, appId, hosts):
  """
  Redeploy application with adding constraints.
  Example:
  ['hostname', 'UNLIKE', '172.31.100.1']
  """
  payload = {}
  constraints = []
  for h in hosts:
    template = ['hostname', 'UNLIKE', str(h)]
    constraints.append(template)
  payload["constraints"] = constraints
  redeploy_url = marathon_endpoint + apps_endpoint + appId
  try:
    response = requests.put(redeploy_url, data=json.dumps(payload))
    print(response.json())
    if response.status_code == 200:
      deploymentId = response.json()['deploymentId']
      wait_for_deployment(marathon_endpoint, deploymentId)
  except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(1)
  return

def migrate_tasks(marathon_endpoint, instances, tasks, hosts):
  """
  Migrate tasks from the hosts going to go for maintenance
  """
  for appId in tasks.iterkeys():
    print(">>> Migrating the following tasks")
    print(appId)

    # Redeploy all the applications running on maintenance hosts by adding constraints
    redeploy_with_constraints(marathon_endpoint, appId, hosts)

    print(">>> Migrated all the tasks")

def main():
  args = parse_args()
  maintenance_hosts = args.hosts.split(',')

  # Get the running marathon application dictionary
  running_instances = get_marathon_apps(args.url)
  print(">>> Total Running Applications: ")
  print(running_instances)

  running_tasks = {}
  # Get the running marathon application dictionary for all hosts which are going for maintenance
  for maintenance_host in maintenance_hosts:
    tasks = get_marathon_tasks(args.url, maintenance_host)
    print(">>> Running Applications on %s: " % maintenance_host)
    print(tasks)
    running_tasks.update(tasks)

  print(">>> Total Running Application: ")
  print(running_tasks)

  # Tasks migration
  migrate_tasks(args.url, running_instances, running_tasks, maintenance_hosts)

if __name__ == "__main__":
  sys.exit(main())