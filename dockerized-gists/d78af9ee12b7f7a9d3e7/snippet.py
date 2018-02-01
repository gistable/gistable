import requests
import json
import calendar
from datetime import datetime, timedelta

#token from https://api.slack.com/web
_token = "YOUR TOKEN HERE" 
_domain = "YOUR SUB DOMAIN HERE"

if __name__ == '__main__':
    while 1:
        files_list_url = 'https://slack.com/api/files.list'
        date = str(calendar.timegm((datetime.now() + timedelta(-30))
            .utctimetuple()))
        data = {"token": _token, "ts_to": date}
        response = requests.post(files_list_url, data = data)
        if len(response.json()["files"]) == 0:
            break
        for f in response.json()["files"]:
            print "Deleting file " + f["name"] + "..."
            timestamp = str(calendar.timegm(datetime.now().utctimetuple()))
            delete_url = "https://" + _domain + ".slack.com/api/files.delete?t=" + timestamp
            requests.post(delete_url, data = {
                "token": _token, 
                "file": f["id"], 
                "set_active": "true", 
                "_attempts": "1"})
    print "DONE!"