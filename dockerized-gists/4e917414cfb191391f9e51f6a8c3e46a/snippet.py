import re
import boto3
import csv
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')

def get_snapshots():
    return ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']

def volume_exists(volume_id):
    if not volume_id: return ''
    try:
        ec2.describe_volumes(VolumeIds=[volume_id])
        return True
    except ClientError:
        return False

def instance_exists(instance_id):
    if not instance_id: return ''
    try:
        ec2.describe_instances(InstanceIds=[instance_id])
        return True
    except ClientError:
        return False

def image_exists(image_id):
    if not image_id: return ''
    try:
        ec2.describe_images(ImageIds=[image_id,])
        return True
    except ClientError:
        return False

def parse_description(description):
    regex = r"^Created by CreateImage\((.*?)\) for (.*?) "
    matches = re.finditer(regex, description, re.MULTILINE)
    for matchNum, match in enumerate(matches):
        return match.groups()
    return '', ''

def main():
    with open('raport.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'snapshot id',
            'description',
            'started',
            'size',
            'volume',
            'volume exists',
            'instance',
            'instance exists',
            'ami',
            'ami exists'])
        for snap in get_snapshots():
            instance_id, image_id = parse_description(snap['Description'])
            writer.writerow([
                snap['SnapshotId'],
                snap['Description'],
                snap['StartTime'],
                str(snap['VolumeSize']),
                snap['VolumeId'],
                str(volume_exists(snap['VolumeId'])),
                instance_id,
                str(instance_exists(instance_id)),
                image_id,
                str(image_exists(image_id)),
            ])

if __name__ == '__main__':
    main()
