import boto
import boto.exception
import boto.sns
import pprint
import re

def send_push(device_id, body):
    region = [r for r in boto.sns.regions() if r.name==u'eu-west-1'][0]

    sns = boto.sns.SNSConnection(
        aws_access_key_id="YOUR_AWS_ACCESS_KEY_HERE",
        aws_secret_access_key="YOUR_AWS_ACCESS_SECRET_HERE",
        region=region,
    )   
    
    try:
        endpoint_response = sns.create_platform_endpoint(
            platform_application_arn='arn:aws:sns:eu-west-1:123456879:app/APNS_SANDBOX/Myapp_Dev',
            token=device_id,
        )   
        endpoint_arn = endpoint_response['CreatePlatformEndpointResponse']['CreatePlatformEndpointResult']['EndpointArn']
    except boto.exception.BotoServerError, err:
        # Yes, this is actually the official way:
        # http://stackoverflow.com/questions/22227262/aws-boto-sns-get-endpoint-arn-by-device-token
        result_re = re.compile(r'Endpoint(.*)already', re.IGNORECASE)
        result = result_re.search(err.message)
        if result:
            endpoint_arn = result.group(0).replace('Endpoint ','').replace(' already','')
        else:
            raise
            
    print "ARN:", endpoint_arn

    publish_result = sns.publish(
        target_arn=endpoint_arn,
        message=body,
    )
    print "PUBLISH"
    pprint.pprint(publish_result)