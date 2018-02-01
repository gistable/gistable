import httplib
import base64
try:
    import json
except ImportError:
    import simplejson as json

config = {"username": "your-sauce-username",
          "access-key": "your-sauce-api-key"}

base64string = base64.encodestring('%s:%s' % (config['username'], config['access-key']))[:-1]

def set_test_status(jobid, passed=True):
    body_content = json.dumps({"passed": passed})
    connection =  httplib.HTTPConnection("saucelabs.com")
    connection.request('PUT', '/rest/v1/%s/jobs/%s' % (config['username'], jobid),
                       body_content,
                       headers={"Authorization": "Basic %s" % base64string})
    result = connection.getresponse()
    return result.status == 200

set_test_status("your-job-id", passed=True)
