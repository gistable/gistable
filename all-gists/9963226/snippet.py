# http://www.gravityhelp.com/documentation/page/Web_API#Security

import time
import base64
import urllib
import requests
import json
import hmac
from hashlib import sha1

URL_BASE = "https://www.example.com/gravityformsapi/"
API_KEY = "1234"
PRIVATE_KEY = "abcd"


def build_gf_url(
    url_base,
    method,  # "GET"/"POST"/"PUT"/"DELETE"
    route,  # e.g. "forms/1"
    api_key,
    private_key,
    valid_for=300,  # How long the signed request is valid (in seconds)
    query_args=None  # Additional query args appended to URL
):
    expires = int(time.time()) + valid_for
    string_to_sign = "{0}:{1}:{2}:{3}".format(
        api_key,
        method,
        route,
        expires
    )
    sig = hmac.new(private_key, string_to_sign, sha1)
    sig_b64 = base64.b64encode(sig.digest())
    required_args = {
        "api_key": api_key,
        "signature": sig_b64,
        "expires": expires,
    }
    # Create URL here rather than passing a dict to requests avoids
    # double-encoding percent signs
    if query_args:
        query = urllib.urlencode(dict(query_args.items() + required_args.items()))
    else:
        query = urllib.urlencode(required_args)
    return url_base + route + "?" + query


def gf_request(
    route,  # e.g. "forms/1"
    method,  # "GET"/"POST"/"PUT"/"DELETE"
    data=None,  # Request body
    query_args=None,  # Additional query args appended to URL
    url_base=URL_BASE,
    api_key=API_KEY,
    private_key=PRIVATE_KEY
):
    url = build_gf_url(
        url_base,
        method,
        route,
        api_key,
        private_key,
        query_args=query_args
    )
    if data:
        json_data = json.dumps(data)
    else:
        json_data = None
    r = requests.request(method, url, data=json_data)
    return r.json()[u"response"]


#print gf_request("forms/1/entries", "GET", query_args={"paging[page_size]": "1"})
