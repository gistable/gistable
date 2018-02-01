# encoding: utf8                                                                                                                                           1,1           Top# encoding: utf8
import argparse
from datetime import datetime
import json
from random import randint
import requests
import sys
from time import sleep


headers = {
    'app_version': '3',
    'platform': 'ios',
}


fb_id = '{ your fb user id here }'
fb_auth_token = '{ your fb auth token here }'


class User(object):
    def __init__(self, data_dict):
        self.d = data_dict

    @property
    def user_id(self):
        return self.d['_id']

    @property
    def ago(self):
        raw = self.d.get('ping_time')
        if raw:
            d = datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S.%fZ')
            secs_ago = int(datetime.now().strftime("%s")) - int(d.strftime("%s"))
            if secs_ago > 86400:
                return u'{days} days ago'.format(days=secs_ago / 86400)
            elif secs_ago < 3600:
                return u'{mins} mins ago'.format(mins=secs_ago / 60)
            else:
                return u'{hours} hours ago'.format(hours=secs_ago / 3600)

        return '[unknown]'

    @property
    def bio(self):
        try:
            x = self.d['bio'].encode('ascii', 'ignore').replace('\n', '')[:50].strip()
        except (UnicodeError, UnicodeEncodeError, UnicodeDecodeError):
            return '[garbled]'
        else:
            return x

    @property
    def age(self):
        raw = self.d.get('birth_date')
        if raw:
            d = datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S.%fZ')
            return datetime.now().year - int(d.strftime('%Y'))

        return 0

    def __unicode__(self):
        return u'{name} ({age}), {distance}km, {ago}'.format(
            name=self.d['name'],
            age=self.age,
            distance=self.d['distance_mi'],
            ago=self.ago
        )

def auth_token(fb_auth_token, fb_user_id):
    h = headers
    h.update({'content-type': 'application/json'})
    req = requests.post(
        'https://api.gotinder.com/auth',
        headers=h,
        data=json.dumps({'facebook_token': fb_auth_token, 'facebook_id': fb_user_id})
    )
    try:
        return req.json()['token']
    except:
        return None


def recommendations(auth_token):
    h = headers
    h.update({'X-Auth-Token': auth_token})
    r = requests.get('https://api.gotinder.com/user/recs', headers=h)
    if r.status_code == 401 or r.status_code == 504:
        raise Exception('Invalid code')
        print r.content

    if not 'results' in r.json():
        print r.json()

    for result in r.json()['results']:
        yield User(result)


def like(user_id):
    try:
        u = 'https://api.gotinder.com/like/%s' % user_id
        d = requests.get(u, headers=headers, timeout=0.7).json()
    except KeyError:
        raise
    else:
        return d['match']


def nope(user_id):
    try:
        u = 'https://api.gotinder.com/pass/%s' % user_id
        requests.get(u, headers=headers, timeout=0.7).json()
    except KeyError:
        raise


def like_or_nope():
    return 'nope' if randint(1, 100) == 31 else 'like'


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Tinder automated bot')
    parser.add_argument('-l', '--log', type=str, default='activity.log', help='Log file destination')

    args = parser.parse_args()

    print 'Tinder bot'
    print '----------'
    matches = 0
    liked = 0
    nopes = 0

    while True:
        token = auth_token(fb_auth_token, fb_id)

        if not token:
            print 'could not get token'
            sys.exit(0)

        for user in recommendations(token):
            if not user:
                break

            print unicode(user)

            try:
                action = like_or_nope()
                if action == 'like':
                    print ' -> Like'
                    match = like(user.user_id)
                    if match:
                        print ' -> Match!'

                    with open('./liked.txt', 'a') as f:
                        f.write(user.user_id + u'\n')

                else:
                    print ' -> random nope :('
                    nope(user.user_id)

            except:
                print 'networking error %s' % user.user_id

            s = float(randint(250, 2500) / 1000)
            sleep(s)
