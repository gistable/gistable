import boto3
import datetime
import json

config = boto3.client("config")
ec2 = boto3.client("ec2")

def evaluate_flowlog(vpc_id):
    response = ec2.describe_flow_logs(
        Filter=[
            {
                "Name": "resource-id",
                "Values": [
                    vpc_id,
                ]
            },
        ],
    )
    if len(response[u"FlowLogs"]) != 0: return True

def evaluate_compliance(vpc_id):
    if evaluate_flowlog(vpc_id):
        return "COMPLIANT"
    else:
        return "NON_COMPLIANT"

def lambda_handler(event, context):
    invocation_event = json.loads(event["invokingEvent"].encode("ascii"))
    ordering_timestamp = invocation_event["notificationCreationTime"]
    vpc_id = invocation_event["configurationItem"]["resourceId"]
    resource_type = invocation_event["configurationItem"]["resourceType"]
    result_token = event["resultToken"]
    compliance = evaluate_compliance(vpc_id)
    responce = config.put_evaluations(
        Evaluations=[
            {
                "ComplianceResourceType": resource_type,
                "ComplianceResourceId": vpc_id,
                "ComplianceType": compliance,
                "OrderingTimestamp": ordering_timestamp
            },
        ],
        ResultToken=result_token
    )