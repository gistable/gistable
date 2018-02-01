import boto3


def as_get_instances(client, asgroup, NextToken = None):
    # this is downright ridiculous because boto3 sucks

    irsp = None
    if NextToken:
        irsp = client.describe_auto_scaling_instances(MaxRecords=2, NextToken=NextToken)
    else:
        irsp = client.describe_auto_scaling_instances(MaxRecords=2)

    for i in irsp['AutoScalingInstances']:
        if i['AutoScalingGroupName'] == asgroup:
            yield i['InstanceId']

    if 'NextToken' in irsp:
        for i in as_get_instances(client, asgroup, NextToken = irsp['NextToken']):
            yield i


if __name__ == '__main__':
    client = boto3.client('autoscaling', region_name='us-east-1')
    print(list(as_get_instances(client, 'content_server')))