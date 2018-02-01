# quick & dirty export of workouts to *.gpx file with timestamps from MapMyFitness API
# for purpose of moving to other apps (tested with Endomondo)
# based on: https://developer.mapmyapi.com/docs/read/Authentication2
# needs API access request "Request a key" @ https://developer.mapmyapi.com/
from __future__ import unicode_literals
import requests
import urlparse
import webbrowser
import json
from requests_oauthlib import OAuth2
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
import sys, os
import pytz
from dateutil.parser import parse

import gpxpy
import gpxpy.gpx

LIMIT_WORKOUTS = 100 # no paging

# get access token for api
client_id = 'CLIENT_ID'
client_secret = 'SECRET'
redirect_uri = 'http://localhost.mapmyapi.com:12345/callback'
authorize_url = 'https://www.mapmyfitness.com/v7.0/oauth2/authorize/?client_id=%s&response_type=code&redirect_uri=%s' % (client_id, redirect_uri)

webbrowser.open(authorize_url)

class AuthorizationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'OK')
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.server.path = self.path
server_address = (urlparse.urlparse(redirect_uri).hostname, urlparse.urlparse(redirect_uri).port)
httpd = HTTPServer(server_address, AuthorizationHandler)
httpd.handle_request()
httpd.server_close()
callback_url = urlparse.urlparse(httpd.path)
authorize_code = urlparse.parse_qs(callback_url.query)['code'][0]

access_token_url = 'https://oauth2-api.mapmyapi.com/v7.0/oauth2/access_token/'
access_token_data = {'grant_type': 'authorization_code', 'client_id': client_id, 'client_secret': client_secret, 'code': authorize_code}
response = requests.post(url=access_token_url, data=access_token_data, headers={'Api-Key': client_id})
access_token = response.json()
oauth = OAuth2(client_id=client_id, token={'token_type': 'Bearer','access_token': access_token['access_token']})

# get workout data
def get_response_json(url):
    response = requests.get(url=url, auth=oauth, verify=False, headers={'Api-Key': client_id})
    return response.json()

self_url = 'https://oauth2-api.mapmyapi.com/v7.0/user/self/'
user_id = get_response_json(self_url)['_links']['self'][0]['id']

workouts_url = 'https://oauth2-api.mapmyapi.com/v7.0/workout/?user={0}&limit={1}&offset=0'.format(user_id, LIMIT)
workout_url = 'https://oauth2-api.mapmyapi.com/v7.0/workout/{0}/?field_set=time_series'

workouts_list = get_response_json(workouts_url)
workouts = []
for workout in workouts_list['_embedded']['workouts']:
    workout_id = workout['_links']['self'][0]['id']
    workout_data = get_response_json(workout_url.format(workout_id))
    workouts.append(workout_data)

# create gpx file from workouts data
gpx = gpxpy.gpx.GPX()

for workout in workouts:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    if workout['has_time_series']:
        start_time = parse(workout['start_datetime'])
        for point in workout['time_series']['position']:
            lat = point[1]['lat']
            lng = point[1]['lng']
            elev = point[1]['elevation']
            time = start_time + timedelta(seconds=round(point[0]))
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lng, elevation=elev, time=time))

print gpx.to_xml()
# python mmr_workout_gpx_export.py > export.gpx