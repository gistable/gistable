import requests, os, glob, json, sys, webbrowser

you = 'self'
data = 'checkins'

try: os.mkdir(data)
except Exception: pass

cid = 'YOUR_CLIENT_ID'

if len(sys.argv) < 2:
    webbrowser.open("""https://foursquare.com/oauth2/authenticate?client_id=%s&response_type=token&redirect_uri=%s""" % (cid, 'http://localhost:8000/'))
else:
    token = sys.argv[1]

def run(offset = 0):
    already = glob.glob("%s/*.json" % data)
    start = 'https://api.foursquare.com/v2/users/%s/checkins?oauth_token=%s&limit=100&offset=%s' % (you, token, offset)
    r = requests.get(start)
    has_new = False
    for t in r.json['response']['checkins']['items']:
        if ("%s/%s.json" % (data, t['id'])) not in already:
            json.dump(t, open('%s/%s.json' % (data, t['id']), 'w'))
            has_new = True
    if has_new:
        run(offset + 100)

print 'starting 4sq archive of @%s' % you
run()
