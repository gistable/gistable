# Instructions:
# 1. Go to https://[yourdomain].slack.com/services/new
# 2. Configure a new Incoming WebHook and paste the URL below on Line 14
# 3. Copy this file into $SPLUNK_HOME$/bin/scripts
# 4. Configure your saved search to run slack_alert.py


import httplib, json
import getopt, sys, os
import subprocess


def main():
  WEBHOOK_URL = [INSERT_URL_HERE]
  headers = {'Content-Type': 'application/json'}

  text = '%s: <%s|Click here> for more details.' % (sys.argv[4], sys.argv[6])
  color = 'good'
  message = {
    'username': 'Splunk',
    'fallback': text,
    'pretext': text,
    'color': color,
    'icon_url': 'https://d38o4gzaohghws.cloudfront.net/static/image/default_icon.png',
    'fields': [
      {
        'title': "Events",
        'value': sys.argv[1],
        'short': True
      }
    ]
  }

  connection = httplib.HTTPSConnection('hooks.slack.com')
  connection.request('POST', WEBHOOK_URL, json.dumps(message), headers)
  print json.dumps(message)
  response = connection.getresponse()
  print response.read().decode()

if __name__ == '__main__':
  main()