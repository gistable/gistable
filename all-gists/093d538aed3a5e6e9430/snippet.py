import re
import urllib
import urllib2
import json

with open('contacts.vcf', 'r') as f:
    vcf = f.read()

    for match in re.finditer(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4})', vcf):
        email =  match.group()

        api_base = 'https://haveibeenpwned.com/api/v2/breachedaccount/%s?truncateResponse=true'
        req = urllib2.Request(api_base % urllib.quote_plus(email))
        try:
            resp = urllib2.urlopen(req)
        except urllib2.HTTPError as e:
            continue
        except urllib2.URLError as e:
            continue

        breaches = json.loads(resp.read())

        for breach in breaches:
            print '%s: %s' % (email, breach['Name'])
