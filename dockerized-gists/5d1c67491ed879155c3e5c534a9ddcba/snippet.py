#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Jamf Pro - Determine Execution Environment
"""

import os

def is_running_directly():
    """
    Returns True if script is being run directly from within a policy;
    False if script is being run from a policy called by another policy.
    """
    if int(os.environ['SHLVL']) >= 2:
        return False
    else:
        return True


def is_running_in_self_service():
    """
    Returns True if the execution environment of this script is from within
    Self Service, false if otherwise

    Thanks to @macmule
    https://github.com/dataJAR/jamJAR/blob/master/script/jamJAR.py#L96
    """
    if not os.environ.get('USERNAME') and os.environ.get('USER'):
        return True
    else:
        return False


def main():
    """
    Main
    """
    print os.environ
    if is_running_directly():
        if is_running_in_self_service():
            # Script is running from a policy intiated by a user from within
            # Self Service
            pass
        else:
            # Script is running directly in a policy that was initiated by one
            # of the "standard" event triggers: Startup, Network State Change,
            # or Enrollment Complete
            pass
    else:
        # Script is running in a policy that was called by another policy
        # ie. - this script runs in Policy B. 
        #     - Policy A called "jamf policy -id $policy_b_id"
        #
        # OR
        #
        # Script is running from a policy triggered by the Login or Logout
        # hook
        pass


if __name__ == '__main__':
    main()