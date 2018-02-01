#!/usr/bin/env python
# encoding: utf-8
import subprocess, string, json, urllib
# DISABLED: import httplib, base64

"""
In order to run this Python script, make it executable first using:
    chmod +x <filename>.py

And then run it using
    ./<filename>.py
"""

# Settings:
username     = "mail@host.tld"
password     = "***"
api_token    = "12345"
hostname     = "host.dynvpn.de"
update_url   = "api.twodns.de/hosts/%s" % hostname
time_to_life = 86400
wildcard     = "false"
get_ip_url   = "api.ipify.org"


def get_public_ip():
    """
    Gets the public IP Address of the computer this script is running on.
    """
    return urllib.urlopen("http://" + get_ip_url).read()
    
    ####################################################
    # httplib Version (NOT working)
    ####################################################
    """
    http_conn = httplib.HTTPConnection(get_ip_url)
    MyPublicIp = http_conn.getresponse()
    http_conn.close()
    return MyPublicIp
    """

def main():
    """
    Update Two-DNS Dynamic DNS with the public IP Address of the computer
    that this script is currently running on.
    
    Example 'curl'-call:
    $ curl -vX PUT -u "mail@host.tld:api_token" -H "Content-Type: application/json" --data '{"ip_address": "127.0.0.1", "activate_wildcard": "false"}' https://api.twodns.de/hosts/host.dynvpn.de
    """
    data = json.dumps({ "ip_address" : get_public_ip(),
                        "activate_wildcard" : wildcard })
    
    ####################################################
    # curl version (working)
    ####################################################
    auth_curl = '%s:%s' % (username, api_token)
    headers_curl = "Content-Type: application/json"
    update_url_curl = "https://" + update_url
    curl_cmd = 'curl -isX PUT -u "%s" -H "%s" --data \'%s\' %s' % (auth_curl, headers_curl, data, update_url_curl)
    sp = subprocess.Popen(curl_cmd, shell=True)
    output, err = sp.communicate()
    print "Response: ", output, "\nErrors: ", err
    
    
    ####################################################
    # httplib Version (NOT working)
    ####################################################
    """
    # base64 encode the username and password
    #auth_b64 = base64.standard_b64encode('%s:%s' % (username, password)).replace('\n', '')
    
    
    # Write the Authorization header like: 'Basic base64encode(username + ':' + password)
    #headers = { "Content-Type": "application/json", "Authorization": "Basic %s" % auth_b64 }
    
    #http_conn = httplib.HTTPConnection(update_url)
    #http_conn.set_debuglevel(1)
    
    #http_conn.request('PUT', update_url + hostname, data, headers=headers)
    # EXAMPLE: send: u'PUT /api/v1/table/10/ HTTP/1.1\r\nHost: localhost:8000\r\nAccept-Encoding: identity\r\nContent-Length: 148\r\nContent-type: application/json\r\nAuthorization: ApiKey: api:79910a14-a82c-41f9-bb79-458247e6b31a\r\n\r\n{"username": "johnny", "type": "admin_user", "resource_uri": "/api/v1/table/10/"}'
    
    #http_response = http_conn.getresponse()
    #print http_response.status, http_response.reason
    #http_conn.close()
    """
    
if __name__ == '__main__':
    main()
    """
    Credit where credit is due:
    1) Two-DNS API Documentation: https://www.twodns.de/de/api
    2) demophoon/ddns.py GitHub Gist: https://gist.github.com/demophoon/bc6b5bea6f39de724934
    3) Python - Using httplib to PUT JSON data: http://stackoverflow.com/questions/25334017/python-using-httplib-to-put-json-data
    4) Python HTTP Basic authentication with httplib: http://mozgovipc.blogspot.ch/2012/06/python-http-basic-authentication-with.html
    5) Python Execute Unix / Linux Command Examples: http://www.cyberciti.biz/faq/python-execute-unix-linux-command-examples/
    """