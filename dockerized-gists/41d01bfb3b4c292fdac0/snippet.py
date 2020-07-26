import boto3
import datetime

def lambda_handler(event, context):
    print("Connecting to RDS")
    client = boto3.client('rds')
    
    print("RDS snapshot backups stated at %s...\n" % datetime.datetime.now())
    client.create_db_snapshot(
        DBInstanceIdentifier='web-platform-subordinate', 
        DBSnapshotIdentifier='web-platform-%s' % datetime.datetime.now().strftime("%y-%m-%d-%H"),
        Tags=[
            {
                'Key': 'CostCenter',
                'Value': 'web'
            },
        ]
    )
    
    for snapshot in client.describe_db_snapshots(DBInstanceIdentifier='web-platform-subordinate', MaxRecords=50)['DBSnapshots']:
        if create_ts < datetime.datetime.now() - datetime.timedelta(days=7):
            print "Deleting snapshot id:", snapshot['DBSnapshotIdentifier']
            client.delete_db_snapshot(
                DBSnapshotIdentifier=snapshot['DBSnapshotIdentifier']
            )