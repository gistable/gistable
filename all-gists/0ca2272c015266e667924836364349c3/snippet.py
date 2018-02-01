#!/usr/bin/env python3
""" Handles validation of a JWT web-token passed by the client
"""
import os
import sys
import argparse

import requests

import simplejson as json

from jose import jwt, JWTError


def pool_url(aws_region, aws_user_pool):
    """ Create an Amazon cognito issuer URL from a region and pool id

    Args:
        aws_region (string): The region the pool was created in.
        aws_user_pool (string): The Amazon region ID.

    Returns:
        string: a URL
    """
    return (
        "https://cognito-idp.{}.amazonaws.com/{}".
        format(aws_region, aws_user_pool)
    )
# def pool_url


def get_client_id_from_access_token(aws_region, aws_user_pool, token):
    """ Pulls the client ID out of an Access Token
    """
    claims = get_claims(aws_region, aws_user_pool, token)
    if claims.get('token_use') != 'access':
        raise ValueError('Not an access token')

    return claims.get('client_id')

# def get_client_id


def get_client_id_from_id_token(token):
    """ Pulls the audience (client id) out of an id_token
    """
    # header, payload, _ = get_token_segments(token)
    payload = jwt.get_unverified_claims(token)
    return payload.get('aud')

# def get_client_id


def get_user_email(aws_region, aws_user_pool, client_id, id_token):
    """ Pulls the user email out of an id token
    """
    if client_id is None:
        client_id = os.environ.get('AWS_CLIENT_ID')

    if client_id is None:
        client_id = get_client_id_from_id_token(id_token)

    claims = get_claims(aws_region, aws_user_pool, id_token, client_id)
    if claims.get('token_use') != 'id':
        raise ValueError('Not an ID Token')

    return claims.get('email')

# def get_user_email


def get_claims(aws_region, aws_user_pool, token, audience=None):
    """ Given a token (and optionally an audience), validate and
    return the claims for the token
    """
    # header, _, _ = get_token_segments(token)
    header = jwt.get_unverified_header(token)
    kid = header['kid']

    verify_url = pool_url(aws_region, aws_user_pool)

    keys = aws_key_dict(aws_region, aws_user_pool)

    key = keys.get(kid)

    kargs = {"issuer": verify_url}
    if audience is not None:
        kargs["audience"] = audience

    claims = jwt.decode(
        token,
        key,
        **kargs
    )

    return claims

# def get_claims


def aws_key_dict(aws_region, aws_user_pool):
    """ Fetches the AWS JWT validation file (if necessary) and then converts
    this file into a keyed dictionary that can be used to validate a web-token
    we've been passed

    Args:
        aws_user_pool (string): the ID for the user pool

    Returns:
        dict: a dictonary of values
    """
    filename = os.path.abspath(
        os.path.join(
            os.path.dirname(sys.argv[0]), 'aws_{}.json'.format(aws_user_pool)
        )
    )

    if not os.path.isfile(filename):
        # If we can't find the file already, try to download it.
        aws_data = requests.get(
            pool_url(aws_region, aws_user_pool) + '/.well-known/jwks.json'
        )
        aws_jwt = json.loads(aws_data.text)
        with open(filename, 'w+') as json_data:
            json_data.write(aws_data.text)
            json_data.close()

    else:
        with open(filename) as json_data:
            aws_jwt = json.load(json_data)
            json_data.close()

    # We want a dictionary keyed by the kid, not a list.
    result = {}
    for item in aws_jwt['keys']:
        result[item['kid']] = item

    return result
# def aws_key_dict


def env_with_error(val, message, default=None):
    """ Tries to fetch a value from the environment and throws an arror if it's
    missing.  Used so that we can return a better error message

    Args:
        val (string); The value to fetch from the environment
        message (string): The message to raise
        default (string): An optional default value.
    Returns:
        string: The value from the environment
    """
    result = os.environ.get(val)
    if result is None:
        result = default

    if result is None:
        raise KeyError(message)
    return result
# def get_with_error


def run_test():
    """ Validates an identity token passed in as an argument.
    We can get the client_id from one of three places.  If we're
    passed an access token, we can get the client_id from that.
    If we're passed a client_id, we'll use it.  If we're given
    neither an access token nor a client_id as an argument, we'll
    look for something in the environemnt.  If that isn't set,
    we'll use the client ID passed as the audience in the identity
    token itself.
    """

    # pylint: disable=missing-docstring,too-few-public-methods
    class Bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    parser = argparse.ArgumentParser(
        description='Validates an AWS id token and prints the email address.')

    parser.add_argument(
        '-c', '--client_id',
        help='The application id to which the id_token applies',
        metavar='<client_id>',
        dest='client_id'
    )

    parser.add_argument(
        '-a', '--access_token',
        help='An access token returned from the authentication authority' +
        ' used to retrieve an client_id',
        metavar='<access_token>',

    )

    parser.add_argument(
        '-r', '--aws_region',
        help='The AWS Region that the pool is defined for. (ie. us-west-2)',
        metavar='<aws_region>',
        dest='aws_region'
    )

    parser.add_argument(
        '-p', '--aws_pool',
        help='The AWS Pool ID that token comes from.',
        metavar='<aws_pool_id>',
        dest='aws_pool'
    )

    parser.add_argument(
        'id_token',
        nargs=1,
        help='The ID token to be validated and have the email address printed',
        metavar='<id_token>'
    )

    args = parser.parse_args()

    aws_region = env_with_error(
        "AWS_REGION", 'Missing AWS_REGION environment variable',
        args.aws_region
    )

    aws_pool = env_with_error(
        "AWS_USER_POOL", 'Missing AWS_USER_POOL environment variable',
        args.aws_pool
    )

    client_id = None
    if args.client_id is not None:
        client_id = args.client_id
    elif args.access_token is not None:
        client_id = get_client_id_from_access_token(
            aws_region, aws_pool, args.access_token)
    try:
        print(
            Bcolors.OKGREEN + Bcolors.BOLD + "SUCCESS: " + Bcolors.ENDC +
            get_user_email(aws_region, aws_pool, client_id, args.id_token[0]))
    except JWTError as error:
        print(
            Bcolors.BOLD + Bcolors.FAIL + "FAILED: " + Bcolors.ENDC +
            str(error))

# def run_test

if __name__ == '__main__':
    run_test()
