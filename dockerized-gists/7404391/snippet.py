#!/usr/bin/env python

"""Sample code for authenticating and requesting data from D&B Direct API.  See
http://developer.dnb.com/ for more information.
"""

import requests  # pip install requests

# Register at http://developer.dnb.com/register-v2
DNB_USERNAME = ""
DNB_PASSWORD = ""


def get_dnb_token(username, password, url="https://maxcvservices.dnb.com/rest/Authentication"):
    """Get a new authentication token.

    See http://developer.dnb.com/docs/2.0/common/authentication-process

    :param username: D&B username
    :type username: str
    :param password: D&B password
    :type password: str
    :returns: authentication token or "INVALID CREDENTIALS"
    :rtype: str
    """
    r = requests.post(
        url,
        headers={
            "x-dnb-user": username,
            "x-dnb-pwd": password,
        }
    )
    return r.headers["Authorization"]


def get_rtng_trnd(duns, token):
    """ Get a D&B Rating & Trend

    See http://developer.dnb.com/docs/2.0/assessment/3.0/ratings

    :param duns: DUNS number
    :type token: str
    :param token: authentication token
    :type token: str
    :returns: dict
    :rtype: dict
    """
    url = "https://maxcvservices.dnb.com/V3.0/organizations/%s/products/RTNG_TRND"
    headers = {"Authorization": token}
    r = requests.get(url % duns, headers=headers)
    return r.json()["OrderProductResponse"]


if __name__ == '__main__':
    token = get_dnb_token(DNB_USERNAME, DNB_PASSWORD)
    sample_duns = "804735132"  # Gorman Manufacturing
    print get_rtng_trnd(sample_duns, token)
