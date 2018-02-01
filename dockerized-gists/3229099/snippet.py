import requests, os, glob, json, codecs

# requires requests. pip install requests

you = 'tmcw'
data = 'gists'

try: os.mkdir(data)
except Exception: pass

def run(page = 1):
    print 'on page %s' % page
    already = glob.glob("%s/*.json" % data)
    start = 'https://api.github.com/users/%s/gists' % you
    if page:
        start = '%s?page=%s' % (start, page)
    r = requests.get(start)
    has_new = False
    for t in r.json:
        if ("%s/%s.json" % (data, t['id'])) not in already:
            print 'downloading %s' % t['id']
            json.dump(t, open('%s/%s.json' % (data, t['id']), 'w'))
            for f, v in t['files'].items():
                fi = requests.get(v['raw_url'])
                print 'downloading %s/%s_%s' % (data, t['id'], f.encode('ascii', 'ignore'))
                codecs.open(u'%s/%s_%s' % (data, t['id'], v['filename']), 'w').write(fi.text.encode('utf-8'))
            has_new = True
        else:
            print '%s already stored' % t['id']
    if has_new and 'next' in r.headers['Link']:
        run(page + 1)

print 'starting gist archive of @%s' % you
run()
