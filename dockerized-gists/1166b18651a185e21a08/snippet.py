import boto3
import logging
import json
import gzip
import urllib
import time
from StringIO import StringIO

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def lambda_handler(event, context):
    
    #set the name of the S3 bucket
    bucketS3 = 'test-flowlogs'
    folderS3 = 'ArcSight'
    prefixS3 = 'AW1Logs_'
    
    #capture the CloudWatch log data
    outEvent = str(event['awslogs']['data'])
    
    #decode and unzip the log data
    outEvent = gzip.GzipFile(fileobj=StringIO(outEvent.decode('base64','strict'))).read()
    
    #convert the log data from JSON into a dictionary
    cleanEvent = json.loads(outEvent)
    
    #create a temp file
    tempFile = open('/tmp/file', 'w+')
    
    #Create the S3 file key
    key = folderS3 + '/' + prefixS3 + str(int(time.time())) + ".log"
    
    #loop through the events line by line
    for t in cleanEvent['logEvents']:
        
        #Transform the data and store it in the temp file. 
        tempFile.write("CEF:0|AWS CloudWatch|FlowLogs|1.0|src=" + str(t['extractedFields']['srcaddr']) + "|spt=" + str(t['extractedFields']['srcport']) + "|dst=" + str(t['extractedFields']['dstaddr']) + "|dpt=" + str(t['extractedFields']['dstport'])+ "|proto=" + str(t['extractedFields']['protocol'])+ "|start=" + str(t['extractedFields']['start'])+ "|end=" + str(t['extractedFields']['end'])+ "|out=" + str(t['extractedFields']['bytes'])+"\n")

    #close the temp file
    tempFile.close()    
    
    #write the files to s3
    s3Results = s3.upload_file('/tmp/file', bucketS3, key)
    print s3Results