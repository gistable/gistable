import sys
import requests
import json
import calendar
from datetime import datetime, timedelta

# This script will download, then delete the non-external files older than 14 days.

_token = "" # administrator token, from https://api.slack.com/web
_project = "" # project name, from http://[project].slack.com
_timewindow = -14 # number of days
_skipExternal = True

def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return local_filename


if __name__ == '__main__':

    if not _token:
        sys.stderr.write("Token is required to continue. Get it at https://api.slack.com/web. You need to be an Administrator")
        sys.exit()

    if not _project:
        sys.stderr.write("Name of your project required to continue. It comes from the URL of your Slack messages: http://[project].slack.com")
        sys.exit()

    raw_input("This will download and delete the Slack files older than " + str(_timewindow * -1) + " days. Press any key to continue, or Ctrl-C to cancel")

    files_list_url = 'https://slack.com/api/files.list'
    date = str(calendar.timegm((datetime.now() + timedelta(_timewindow))
        .utctimetuple()))
    data = {
        "token": _token,
        "ts_to": date,
        "count": 1000
        }
    response = requests.post(files_list_url, data = data)
    for f in response.json()["files"]:
        if _skipExternal and f["is_external"]:
            continue

        download_file(f["url"])

        print "Deleting file " + f["name"] + "..."
        timestamp = str(calendar.timegm(datetime.now().utctimetuple()))
        delete_url = "https://" + _project + ".slack.com/api/files.delete?t=" + timestamp
        result = requests.post(delete_url, data = {
            "token": _token,
            "file": f["id"],
            "set_active": "true",
            "_attempts": "1"})

        message = result.json()
        if not message["ok"]:
            print message["error"]