import boto3
import logging
from datetime import *

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.WARNING)

#define the connection
ec2 = boto3.resource('ec2', region_name="us-west-2")
sns = boto3.resource('sns')
platform_endpoint = sns.PlatformEndpoint('[your SNS arn here]')

#set the date to today for the snapshot
today = datetime.now().date()

def lambda_handler(event, context):
    
    #collect all volumes in a region
    volumes = ec2.volumes.all()
    
    #report header
    missingReport = "The Following Volumes are Orphaned: \n"
    x = 0
    
    #loop through by volumes
    for vol in volumes:
        if vol.state == "available":
            missingReport = missingReport + "- " + str(vol.id) + " - Size: " + str(vol.size) + " - Created: " + str(vol.create_time) + "\n"
            x= x + 1
    
    #only send a report if there are orphanes
    if x == 0:
        print "Nothing to Report"
    else:
        response = platform_endpoint.publish(
            Message=missingReport,
            Subject='Orphaned Volume Report: ' + str(today),
            MessageStructure='string',
        )
        
        print missingReport