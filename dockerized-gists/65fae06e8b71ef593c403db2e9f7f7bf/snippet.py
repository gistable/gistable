#!/usr/bin/env python

"""Convert CSV policies into AWS JSON format."""

import json
import csv

POLICIES = 'terraform.csv'
CRUD_COL = 2
ACTION_COL = 3
POLICIES_COL_COUNT = 8

TEMPLATE = """{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
"""

CREATE_OPS = {'CREATE', 'READ', 'UPDATE'}
DELETE_OPS = {'DELETE', 'READ', 'UPDATE'}

INSTANCE_CREATE_FILE = 'instance-create.json'
INSTANCE_DELETE_FILE = 'instance-delete.json'


def parse_policies():
    policies = {'CREATE': set(), 'DELETE': set()}
    with open(POLICIES) as fp:
        csv_policies = csv.reader(fp)
        for row in csv_policies:
            if len(row) < POLICIES_COL_COUNT:
                continue
            operation = row[CRUD_COL]
            ec2action = row[ACTION_COL]
            if operation in CREATE_OPS:
                policies['CREATE'].add(ec2action)
            if operation in DELETE_OPS:
                policies['DELETE'].add(ec2action)
    return policies


def save_policies(policies):
    create = json.loads(TEMPLATE)
    create['Statement'][0]['Action'] = sorted(policies['CREATE'])
    delete = json.loads(TEMPLATE)
    delete['Statement'][0]['Action'] = sorted(policies['DELETE'])
    with open(INSTANCE_CREATE_FILE, 'w') as fp:
        json.dump(create, fp, indent=4)
    with open(INSTANCE_DELETE_FILE, 'w') as fp:
        json.dump(delete, fp, indent=4)


if __name__ == '__main__':
    policies = parse_policies()
    save_policies(policies)