import argparse
from mock import Mock

m = Mock()

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

query_group = subparsers.add_parser('query')
add_group = subparsers.add_parser('add')
update_group = subparsers.add_parser('update')

subparsers = query_group.add_subparsers()
host_query = subparsers.add_parser('host')
host_query.add_argument('host_name')
host_query.set_defaults(func=m.query_host)

profile_query = subparsers.add_parser('profile')
profile_query.add_argument('profile_name')
profile_query.set_defaults(func=m.query_profile)

environment_query = subparsers.add_parser('environment')
environment_query.add_argument('environment_name')
environment_query.set_defaults(func=m.query_environment)

subparsers = add_group.add_subparsers()
host_add = subparsers.add_parser('host')
host_add.add_argument('host_name')
host_add.set_defaults(func=m.add_host)

profile_add = subparsers.add_parser('profile')
profile_add.add_argument('profile_name')
profile_add.set_defaults(func=m.add_profile)

environment_add = subparsers.add_parser('environment')
environment_add.add_argument('environment_name')
environment_add.set_defaults(func=m.add_environment)

subparsers = update_group.add_subparsers()
host_update = subparsers.add_parser('host')
host_update.add_argument('host_name')
host_update.set_defaults(func=m.update_host)

profile_update = subparsers.add_parser('profile')
profile_update.add_argument('profile_name')
profile_update.set_defaults(func=m.update_profile)

environment_update = subparsers.add_parser('environment')
environment_update.add_argument('environment_name')
environment_update.set_defaults(func=m.update_environment)

options = parser.parse_args()
options.func(options)

print m.method_calls