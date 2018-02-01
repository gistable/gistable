from __future__ import print_function

import json

import boto3

ses_client = boto3.client('ses')

TARGET = "mike"

EMAILS = {
    "kaitlyn": "",
    "mike": "XXX@sync.omnigroup.com"
}

def send_email(to_email, task_text):
    response = ses_client.send_email(
        Source='XYXY@gmail.com',
        Destination={
            'ToAddresses': [
                to_email  
            ],
        },
        Message={
            'Subject': {
                'Data': task_text,
            },
            'Body': {
                'Text': {
                    'Data': ""
                }
            }
        }
    )
    
def read_from_echo(event, *args, **kwargs):
    slots = event["request"]["intent"]["slots"]
    task_text = slots["TaskText"]["value"].capitalize()
    send_email(EMAILS[TARGET], task_text)
    
    response = {
        "version": "1.0",
        "sessionAttributes": {},
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Done."
            },
            "shouldEndSession": True
        }
    }

    return response