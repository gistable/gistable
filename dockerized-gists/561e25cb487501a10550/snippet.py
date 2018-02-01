import json, traceback, requests, types
from collections import defaultdict

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

class HypothesisUtils:

    def __init__(self):
        self.query_url = 'https://hypothes.is/api/search?{query}'

    def search_all(self):
        params = {'limit':200, 'offset':0 }
        while True:
            h_url = self.query_url.format(query=urlencode(params))
            r = requests.get(h_url).json()
            rows = r.get('rows')
            params['offset'] += len(rows)
            if len(rows) is 0:
                break
            for row in rows:
                yield row

    @staticmethod
    def get_info_from_row(r):
        updated = r['updated'][0:19]
        user = r['user'].replace('acct:','').replace('@hypothes.is','')
        uri = r['uri'].replace('https://via.hypothes.is/h/','').replace('https://via.hypothes.is/','')

        if r['uri'].startswith('urn:x-pdf') and r.has_key('document'):
            if r['document'].has_key('link'):
                links = r['document']['link']
                for link in links:
                    uri = link['href']
                    if uri.encode('utf-8').startswith('urn:') == False:
                        break
            if uri.encode('utf-8').startswith('urn:') and r['document'].has_key('filename'):
                uri = r['document']['filename']

        if r.has_key('document') and r['document'].has_key('title'):
            t = r['document']['title']
            if isinstance(t, types.ListType) and len(t):
                doc_title = t[0]
            else:
                doc_title = t
        else:
            doc_title = uri
        doc_title = doc_title.replace('"',"'")
        if doc_title == '': doc_title = 'untitled'

        tags = []
        if r.has_key('tags') and r['tags'] is not None:
            tags = r['tags']
            if isinstance(tags, types.ListType):
                tags = [t.strip() for t in tags]

        text = ''
        if r.has_key('text'):
            text = r['text']
        refs = []
        if r.has_key('references'):
            refs = r['references']
        target = []
        if r.has_key('target'):
            target = r['target']

        is_page_note = False
        if refs == [] and target == [] and tags == []: 
            is_page_note = True
        
        if r.has_key('document') and r['document'].has_key('link'):
            links = r['document']['link']
            if type(links) != type(list()):
                links = [{'href':links}]
        else:
            links = []

        return {'updated':updated, 'user':user, 'uri':uri, 'doc_title':doc_title, 
                'tags':tags, 'text':text, 'references':refs, 'target':target, 'is_page_note':is_page_note, 'links':links }


unique_uris = defaultdict(list)
for row in HypothesisUtils().search_all():
    unique_uris[row['uri']].append(row)

report = ''

for uri in unique_uris.keys():
    aliases = set()
    for row in unique_uris[uri]:
        has_doi_alias = False
        if uri != row['uri']:
            continue
        info = HypothesisUtils.get_info_from_row(row)
        for link in info['links']:
            if link.has_key('href') and link['href'] != uri:
                aliases.add(link['href'])
    bundle = ''
    if len(aliases):
        for alias in aliases:
            if alias.startswith('doi:'):
                if has_doi_alias == False:
                    u = '\n%s\n' % uri
                    bundle += u
                    has_doi_alis = True
                a = "\t%s\n" % alias
                bundle += a
    report += bundle

f = open('./aliases.txt','w')
f.write(report.encode('utf-8'))
f.close()
