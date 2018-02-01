#! /usr/local/env python
# coding: utf-8

import gzip
import json
from pprint import pprint
import pandas as pd
from pandas.io.json import json_normalize
import sys
import socket
import boto
import os
import ipaddress
import asyncio
import glob
from urllib.parse import urljoin
from urllib.parse import urlencode
import urllib.request as urlrequest


class Slack():
    
    def __init__(self, url=""):
        self.url = url
        self.opener = urlrequest.build_opener(urlrequest.HTTPHandler())
    
    def notify(self, **kwargs):
        """
        Send message to slack API
        """
        return self.send(kwargs)
    
    def send(self, payload):
        """
        Send payload to slack API
        """
        payload_json = json.dumps(payload)
        data = urlencode({"payload": payload_json})
        req = urlrequest.Request(self.url)
        response = self.opener.open(req, data.encode('utf-8')).read()
        return response.decode('utf-8')


class CloudtrailAnalysis():

    @staticmethod
    def check_value(file_name, df_data, value):
        if df_data[df_data['eventName'] == value].empty:
            pass
        else:
            frame =  df_data[df_data['eventName'] == value]
            #print(df_data[df_data['eventName'] == value])
            try:
                normalized_name = frame['userIdentity.userName'].values[0]
            except:
                normalized_name = "noNameFound"
            result = value, frame['eventTime'].values[0], frame['sourceIPAddress'].values[0], normalized_name
            #print(file_name)
            return result


async def get_file_analyse_local_events(zipped, event, outgoing_message):
    #print("+++ Found new log: ", f)
    with gzip.open(zipped, "rb") as f:
        d = json.loads(f.read().decode("ascii"))
    records = d["Records"]
    df_data = json_normalize(records)
    if CloudtrailAnalysis.check_value(zipped, df_data, event) == None:
        pass
    else:
        outgoing_message.append(CloudtrailAnalysis.check_value(zipped, df_data, event))
        return CloudtrailAnalysis.check_value(zipped, df_data, event)


async def main(unzipped, event, outgoing_message):
    await get_file_analyse_local_events(unzipped, event, outgoing_message)

"""
($.eventName=CreateTrail)
($.eventName=UpdateTrail)
($.eventName=DeleteTrail)
($.eventName=DeleteGroupPolicy)
($.eventName=DeleteRolePolicy)
($.eventName=DeleteUserPolicy)
($.eventName=PutGroupPolicy)
($.eventName=PutRolePolicy)
($.eventName=PutUserPolicy)
($.eventName=CreatePolicy)
($.eventName=DeletePolicy)
($.eventName=CreatePolicyVersion)
($.eventName=DeletePolicyVersion)
($.eventName=AttachRolePolicy)
($.eventName=DetachRolePolicy)
($.eventName=AttachUserPolicy)
($.eventName=DetachUserPolicy)
($.eventName=AttachGroupPolicy)
($.eventName=DetachGroupPolicy)
"""
#security_events = ['ConsoleLogin','CreateKeyPair', 'CheckMfa','PutUserPolicy','DeleteTrail']



# list group of Cloudtrail logs you want processed
hdd_files = glob.glob("/Users/bigsnarfdude/cloudtrail_logs/*.json.gz")
security_events = ['ConsoleLogin']
outgoing_message = []
loop = asyncio.get_event_loop()

for zipped in hdd_files:
    for event in security_events:
        loop.run_until_complete(main(zipped, event, outgoing_message))
loop.close()

deduped = [ str(x) for x in list(set(outgoing_message))]
sort_deduped = deduped.sort()
post = "\n".join(deduped)

# put in the details of your slack webhook
slack = Slack(url="https://hooks.slack.com/services/asdfasdf/qwerqwer/asdfqwerasdfqwer")
slack.notify(text=post, channel="#testing", username="security-bot", icon_emoji=":robot_face:")