"""An AWS lambda function for pushing VPC flow logs to Sumo Logic.

To use this you need to do a few things:

- In the Sumo Logic console create a new Hosted / HTTP collector (https://service.sumologic.com/help/Configuring_an_HTTP_Source.htm)
    - Save the secret URL that is generated, you'll need it below
- Enable flow logs (http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/flow-logs.html)
- Create a new Lambda function. If you're doing this in the console:
    - Skip picking a blueprint
    - Function name: FlowLogsToSumo
    - Runtime: python
    - Code <paste this gist>
    - Edit the code to change the value of ENDPOINT to be the secret HTTP collector endpoint you generated in step 1
    - Handler: lambda_function.lambda_handler
    - Role: Create a new or use an existing basic execution role
    - Memory: 128MB (the minimum)
    - Timeout: I suggest 7 seconds
- Once the function is created, configure an event source
    - Event source type: CloudWatch Logs
    - Filter name: FlowToSumo
    - Filter pattern: leave blank
    
Within a few minutes of enabling the event source you should have flow logs in sumo.

If you use the VPC Flow Logs app in Sumo Logic you'll need to edit panels to fix the
queries. They expect the data to come in via kinesis and this isn't kinesis. The proper
parse for Sumo is::

  | parse "* * * * * * * * * * * * * * *" as timestamp,version,accountID,interfaceID,src_ip,dest_ip,src_port,dest_port,Protocol,Packets,bytes,StartSample,EndSample,Action,status

"""

from botocore.vendored import requests
from base64 import b64decode
from json import loads
from zlib import compress, decompress, MAX_WBITS

ENDPOINT = <Insert HTTP Collector endpoint URL here>

def lambda_handler(event, context):
    data = event.get('awslogs', {}).get('data')
    
    if not data:
        return
    records = loads(decompress(b64decode(data), 16 + MAX_WBITS))
    messages = []
    for log_event in records['logEvents']:
        messages.append("%s %s" % (log_event['timestamp'], log_event['message']))

    headers = {'Content-Encoding': 'deflate'}
    requests.post(ENDPOINT, compress("\n".join(messages)), headers=headers)
    print 'Sent %d messages' % (len(messages),)