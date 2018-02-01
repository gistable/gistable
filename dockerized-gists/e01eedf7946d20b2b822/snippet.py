import boto3
import logging
import json
import gzip
from StringIO import StringIO

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('firehose')

def lambda_handler(event, context):
    
    #capture the CloudWatch log data
    outEvent = str(event['awslogs']['data'])
    
    #decode and unzip the log data
    outEvent = gzip.GzipFile(fileobj=StringIO(outEvent.decode('base64','strict'))).read()
    
    #convert the log data from JSON into a dictionary
    cleanEvent = json.loads(outEvent)
    
    #initiate a list
    s = []
    
    #set the name of the Kinesis Firehose Stream
    firehoseName = 'FlowLogTest'
    
    #loop through the events line by line
    for t in cleanEvent['logEvents']:
        
        #Transform the data and store it in the "Data" field. 
        p={
            #Fields in FlowLogs - [version, accountid, interfaceid, srcaddr, dstaddr, srcport, dstport, protocol, packets, bytes, start, stop, action, logstatus]
            'Data': str(t['extractedFields']['start']) + "," + str(t['extractedFields']['dstaddr']) + "," + str(t['extractedFields']['srcaddr']) + "," + str(t['extractedFields']['packets'])+"\n"
        }
        
        #write the data to our list
        s.insert(len(s),p)
        
        #limit of 500 records per batch. Break it up if you have to.
        if len(s) > 499:
            #send the response to Firehose in bulk
            SendToFireHose(firehoseName, s)
            
            #Empty the list
            s = []
    
    #when done, send the response to Firehose in bulk
    if len(s) > 0:
        SendToFireHose(firehoseName, s)

#function to send record to Kinesis Firehose
def SendToFireHose(streamName, records):
    response = client.put_record_batch(
        DeliveryStreamName = streamName,
        Records=records
    )
    
    #log the number of data points written to Kinesis
    print "Wrote the following records to Firehose: " + str(len(records))