import argparse
import requests
import yaml
import os

def write_yaml_default_assignees(destination_dir, namespace, name, value):
    yaml_namespace_dir = os.path.join(destination_dir, namespace)
    yaml_file_path = os.path.join(yaml_namespace_dir, name)
    print('Writing {0}'.format(yaml_file_path))
    if not os.path.isdir(yaml_namespace_dir):
        os.mkdir(yaml_namespace_dir)
    with open(yaml_file_path, 'w') as yaml_file_stream:
        value = dict(monitoring=value)
        yaml.dump(value, yaml_file_stream, default_flow_style=False)


parser = argparse.ArgumentParser()
parser.add_argument('--pkgdburl', help='Base URL to PkgDB',
                    default='https://admin.fedoraproject.org/pkgdb/')
parser.add_argument('--pagureurl', help='Base URL to Pagure over dist-git',
                    default='https://src.fedoraproject.org/')
parser.add_argument('destinationdir',
                    help='Directory for the repository structure')
args = parser.parse_args()

namespace_to_mf_keys = {
    'rpms': ['Fedora', 'Fedora EPEL'],
    'container': ['Fedora Container'],
    'modules': ['Fedora Modules']
}
pkgdb_mf_url = '{0}/api/package/'.format(
    args.pkgdburl.rstrip('/'))

pagure_projects_url = '{0}/api/0/projects?page=1&per_page=100'.format(
    args.pagureurl.rstrip('/'))
while True:
    pagure_projects_rv = requests.get(pagure_projects_url, timeout=60).json()
    for project in pagure_projects_rv['projects']:
        print('Looking at {0}'.format(project['fullname']))
        # If it's not a namespace we know about, skip it
        if project['namespace'] not in namespace_to_mf_keys:
            continue

        pkgdb_mf_info = requests.get(pkgdb_mf_url+project['name'], timeout=600).json()
        for mf_key in namespace_to_mf_keys[project['namespace']]: 
            pkgdb_mf_status = next(pkg['package']['monitor'] for pkg in pkgdb_mf_info['packages'])
            if not pkgdb_mf_status:
                continue

            yaml_mf = str(pkgdb_mf_status)
            write_yaml_default_assignees(args.destinationdir,
            project['namespace'], project['name'],
            yaml_mf)

    if pagure_projects_rv['pagination']['next']:
        pagure_projects_url = pagure_projects_rv['pagination']['next']
    else:
        break

print('All done!')