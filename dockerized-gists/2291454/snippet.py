import urllib2
from lxml import html
from collections import defaultdict

url   = "http://www.youtube.com/watch?v=IyLZ6RXJ8Eg"
doc   = html.parse(urllib2.urlopen(url))
data  = defaultdict(dict)
props = doc.xpath('//meta[re:test(@name|@property, "^twitter|og:.*$", "i")]',
                  namespaces={"re": "http://exslt.org/regular-expressions"})

for prop in props:
    if prop.get('property'):
        key = prop.get('property').split(':')
    else:
        key = prop.get('name').split(':')
    
    if prop.get('content'):
        value = prop.get('content')
    else:        
        value = prop.get('value')
    
    if not value:
        continue
    value = value.strip()
    
    if value.isdigit():
        value = int(value)
    
    ref = data[key.pop(0)]
    
    for idx, part in enumerate(key):
        if not key[idx:-1]: # no next values
            ref[part] = value
            break
        if not ref.get(part):
            ref[part] = dict()
        else:
            if isinstance(ref.get(part), basestring):
                ref[part] = {'url': ref[part]}
        ref = ref[part]