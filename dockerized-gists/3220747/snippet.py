import requests, os, glob, json

you = 'tmcw'
data = 'tweets'

try: os.mkdir(data)
except Exception: pass

def run(max_id = False):
    already = glob.glob("%s/*.json" % data)
    start = 'http://api.twitter.com/1/statuses/user_timeline.json?screen_name=%s&include_rts=true&count=200' % you
    if max_id:
        start = '%s&max_id=%s' % (start, max_id)
    r = requests.get(start)
    has_new = False
    for t in r.json:
        if ("%s/%s.json" % (data, t['id'])) not in already:
            json.dump(t, open('%s/%s.json' % (data, t['id']), 'w'))
            has_new = True
    if has_new:
        last = r.json.pop()
        run(last['id'])

print 'starting twitter archive of @%s' % you
run()
