#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Follow these steps to configure the webhook in Slack:

  1. Navigate to https://<your-team-domain>.slack.com/services/new

  2. Search for and select "Incoming WebHooks".

  3. Choose the default channel where messages will be sent and click "Add Incoming WebHooks Integration".

  4. Copy the webhook URL from the setup instructions and use it in the next section.


Follow these steps to encrypt your Slack hook URL for use in this function:

  1. Create a KMS key - http://docs.aws.amazon.com/kms/latest/developerguide/create-keys.html.
  
     @hayd note: It seems to be important that the key, role and lambda are all in the same region...

  2. Encrypt the event collector token using the AWS CLI.
     $ aws kms encrypt --key-id alias/<KMS key name> --plaintext "<SLACK_HOOK_URL>"

     Note: You must exclude the protocol from the URL (e.g. "hooks.slack.com/services/abc123").

  3. Copy the base-64 encoded, encrypted key (CiphertextBlob) to the ENCRYPTED_HOOK_URL variable.
  
     @hayd note: This is the output of the above `aws kms encrypt` command verbatim.

  4. Give your function's role permission for the kms:Decrypt action.
     Example:

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt"
            ],
            "Resource": [
                "<your KMS key ARN>"
            ]
        }
    ]
}
'''
from __future__ import print_function

import boto3
import json
import logging
import re

from base64 import b64decode
from urllib2 import Request, urlopen, URLError, HTTPError

# value of the CiphertextBlob key in output of $ aws kms encrypt --key-id alias/<KMS key name> --plaintext "<SLACK_HOOK_URL>"
ENCRYPTED_HOOK_URL = "CiC9..."  

HOOK_URL = "https://" + boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_HOOK_URL))['Plaintext']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Event: " + str(event))

    state_dict = {"Ok": ":thumbsup:", "Info": ":information_source:", "Severe": ":exclamation:"}

    d = dict(line.split(": ") for line in event['Records'][0]['Sns']["Message"].splitlines() if ": " in line)
    
    transition = re.match('Environment health has transitioned from (.*) to (.*?)\.', d['Message'])
    if transition:
        original, became = map(lambda x: state_dict.get(x, x), transition.groups())
        d["Message"] = "*Health*: " + original + u" ⟶ " + became + "\n_" + d["Message"].split(". ", 1)[1] + "_"

    slack_message = {
        'channel': 'build' if "New application version was deployed" in d["Message"] else 'beanstalk',
        'text': d["Message"],
        'username': d["Environment"],
        'icon_emoji': ':tophat:'
    }

    req = Request(HOOK_URL, json.dumps(slack_message))

    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)