#!/usr/bin/env python
'''
Check

    python datahub-new-org -h

Or if it's in your path:

    datahub-new-org -h

Requires ckanapi:

    https://github.com/ckan/ckanapi

'''

import sys 
import os
import argparse

import ckanapi

remote = 'http://datahub.io'
api_key_env_var_name = 'DATAHUB_API_KEY'


def main(api_key, user_name, org_name, org_title):

    ckan = ckanapi.RemoteCKAN(remote, apikey=api_key)

    # Check if user exists
    try:
        ckan.action.user_show(id=user_name)
    except ckanapi.NotFound:
        print('User {0} does not exist in datahub.io'.format(user_name))
        sys.exit(1)

    # Check if org exists
    try:
        ckan.action.organization_show(id=org_name)
        print('Organization {0} already exists in datahub.io'.format(org_name))
        sys.exit(1)
    except ckanapi.NotFound:
        pass

    # Create org
    params = { 
        'title': org_title,
        'name': org_name,
    }   
    org = ckan.action.organization_create(**params)

    # Assign user admin roles
    params = { 
        'id': org['id'],
        'object': user_name,
        'object_type': 'user',
        'capacity': 'admin',
    }

    ckan.action.member_create(**params)

    # Check it worked

    org = ckan.action.organization_show(id=org['id'])
    admin = [user for user in org['users']
             if user['name'] == user_name and user['capacity'] == 'admin']

    assert admin, 'User was not added as organization admin'

    # All good, print email template

    email = '''
Hi,

Your organization '{org_title}' is now created.

After logging in with your user ({user_name}), you can add new datasets here:

http://datahub.io/organization/{org_name}

And edit its details here:

http://datahub.io/organization/edit/{org_name}

Have a nice day!
    '''

    print(email.format(org_name=org_name, org_title=org_title,
                       user_name=user_name))

    sys.exit(0)


if __name__ == '__main__':

    description = '''
Creates a new organization on DataHub.io and sets up a user as its Admin.

If the API key is not provided it will be read from {0}.

If the rest of parameters are not provided you will be prompt for them.

'''.format(api_key_env_var_name)

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-a', '--api_key',
                        help='A valid sysadmin key for DataHub.io')
    parser.add_argument('-u', '--user_name',
                        help='Existing user on DataHub.io')
    parser.add_argument('-t', '--org_title',
                        help='Title of the organization to be created')
    parser.add_argument('-n', '--org_name',
                        help='Name of the organization to be created')

    args = parser.parse_args()

    api_key = args.api_key
    if not api_key:
        api_key = os.environ.get(api_key_env_var_name)
        if not api_key:
            print('No API key provided explicitly or on {0}'.format(
                  api_key_env_var_name))
            sys.exit(1)

    def _check_arg(args, var, prompt):
        if getattr(args, var):
            return getattr(args, var)
        var = raw_input('{0}:'.format(prompt).title())
        if not var:
            print('Please provide a value for the {0}'.format(prompt))
            sys.exit(1)
        return var

    user_name = _check_arg(args, 'user_name', 'DataHub user name')
    org_title = _check_arg(args, 'org_title', 'Organization title')
    org_name = _check_arg(args, 'org_name', 'Organization name (slug)')

    main(api_key, user_name, org_name, org_title)
