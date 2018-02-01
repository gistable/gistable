#coding: utf-8

import requests
import csv
from urllib import parse

access_token = ''
endpoint = 'https://graph.facebook.com/v2.5/%s/insights/post_impressions_unique/'

def get_post_id(url):
    parsed = parse.urlparse(url)
    params = parse.parse_qs(parsed.query)
    id = params.get('id')
    story_fbid = params.get('story_fbid')

    if id and story_fbid:
        return "_".join(id + story_fbid)

    return parsed.path.split('/')[-2]

with open('data.csv') as csvfile:
    reader = csv.reader(csvfile)
    for url in reader:
        facebook_post_id = get_post_id(url[0])
        request_url = endpoint % facebook_post_id
        response = requests.get(request_url, params={'access_token': access_token})
        value = ''
        try:
            value = response.json().get('data')[0].get('values')[0].get('value')
        except:
            pass
        print(url[0] + ',' + str(value))