#!/usr/bin/python

from boto.ec2 import connect_to_region
from boto.ec2.group import Group

def main():
    module = AnsibleModule(
        argument_spec = dict(
            ec2_id         = dict(required=True),
            group_names    = dict(required=True),
            region         = dict(required=True)))
    connection = connect_to_region(module.params.get("region"))
    ec2_id = module.params.get("ec2_id")
    group_names = module.params.get("group_names")

    group_ids = set([group.id for group in connection.get_all_security_groups(group_names)])
    current_group_ids = set([group.id for group in connection.get_instance_attribute(ec2_id, "groupSet")["groupSet"]])
    if connection.modify_instance_attribute(ec2_id, "groupSet", current_group_ids.union(group_ids)):
        current_groups = connection.get_instance_attribute(ec2_id, "groupSet")["groupSet"]
        module.exit_json(changed=True, groups=[group.id for group in current_groups])
    else:
        module.fail_json(msg="Could not update groups")

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
