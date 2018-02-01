import httplib2
import urllib
try:
    import json
except ImportError:
    import simplejson as json

# create a global Http object so we can reuse connections
http = httplib2.Http('.cache')

def search(q, page=1, sections=False, annotations=False):
    """
    Search for documents on DocumentCloud
    """
    base = "http://www.documentcloud.org/api/search.json?"
    params = {
        'q': q,
        'page': page,
        'sections': sections,
        'annotations': annotations
    }
    
    resp, content = http.request(base + urllib.urlencode(params))
    results = json.loads(content)
    return results.get('documents')
