#!/usr/bin/env python
import os
import sys
import pickle
from datetime import datetime, timedelta, tzinfo

import boto3
import botocore


credentials_cache_file = ".aws_credentials.cache"


class UTC(tzinfo):
    """UTC"""
    def utcoffset(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return timedelta(0)


def get_credentials(profile):
    try:
        with open(credentials_cache_file) as f:
            cache = pickle.load(f)
    except IOError:
        # No or corrupt file.
        cache = {}

    if profile in cache:
        creds, expiry = cache[profile]
        if expiry > datetime.now(UTC()):
            return creds

    try:
        session = boto3.Session(profile_name=profile)
    except botocore.exceptions.ProfileNotFound:
        print "Environment \"%s\" does not exist in configuration. Aborting..." % (profile,)
        sys.exit(1)

    cred = session.get_credentials()

    cache[profile] = (cred.get_frozen_credentials(), cred._expiry_time)
    with open(credentials_cache_file, "w") as f:
        pickle.dump(cache, f)

    return cred


def args():
    # If this script is invoked with a different name, say through a
    # symlink, use that name as the profile. Otherwise use first arg.
    invoked_name = os.path.basename(sys.argv.pop(0))
    if invoked_name != "awsudo.py":
        profile = invoked_name
    else:
        profile = sys.argv.pop(0)

    return profile, sys.argv


def run_program(credentials, argv):
    env = os.environ.copy()
    env.update(AWS_ACCESS_KEY_ID=credentials.access_key,
               AWS_SECRET_ACCESS_KEY=credentials.secret_key,
               AWS_SESSION_TOKEN=credentials.token)

    os.execvpe(argv[0], argv, env)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "Usage: %s <profile> <command> [<argument> ...]" % tuple(sys.argv)
        sys.exit(1)
    profile, argv = args()
    print "Using environment \"%s\":" % (profile,)
    creds = get_credentials(profile)
    run_program(creds, argv)
