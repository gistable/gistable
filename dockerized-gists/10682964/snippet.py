#!/usr/bin/env python
"""
Launch an AWS Web Console.

Usage:
  awsconsole launch --role=<role_arn> [--profile=<profile_name>]

Commands:
  launch - Launch the AWS Console in your default web browser with
           the specified credentials.  The console will be authenticated
           using the IAM Role you specify with the --role option.

"""

import webbrowser
from urllib import urlencode

from docopt import docopt

import botocore.session
import botocore.vendored.requests
from botocore.compat import json

issuer_url = 'https://mysignin.internal.mycompany.com/'
console_url = 'https://console.aws.amazon.com/'
sign_in_url = 'https://signin.aws.amazon.com/federation'


def launch_cmd(role_arn, profile=None):
    session = botocore.session.get_session()
    session.profile = profile
    sts = session.get_service('sts')
    endpoint = sts.get_endpoint()
    op = sts.get_operation('AssumeRole')
    creds = op.call(endpoint, role_arn=role_arn, role_session_name='foobar')[1]
    d = {'sessionId': creds['Credentials']['AccessKeyId'],
         'sessionKey': creds['Credentials']['SecretAccessKey'],
         'sessionToken': creds['Credentials']['SessionToken']}
    json_str = json.dumps(d)
    params = {'Action': 'getSigninToken',
              'Session': json_str}
    r = botocore.vendored.requests.get(sign_in_url, params=params)
    d = json.loads(r.text)
    d['Action'] = 'login'
    d['Issuer'] = issuer_url
    d['Destination'] = console_url
    uri = sign_in_url + '?' + urlencode(d)
    webbrowser.open(uri)


if __name__ == '__main__':
    args = docopt(__doc__, version='awsconsole 0.1')
    if args['launch']:
        launch_cmd(args.get('--role'), args.get('--profile'))
