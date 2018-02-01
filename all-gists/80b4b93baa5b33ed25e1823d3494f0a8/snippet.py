# Usage: ./dns_check.py <list_of_domain_names.txt>
import dns.resolver
import requests
import re
import json
import sys

resolver = dns.resolver.Resolver()
resolver.timeout = 5
resolver.lifetime = 5

def is_available(domain):
  try:
    hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
    r = requests.get('https://njal.la/list/?search=' + domain, headers=hdr)
    search = re.search('var results = \[(.*)\];', r.text)
    if search:
      domain = json.loads(search.group(1))
      print(domain)
      if domain['status'] == 'available':
      	return True
  except:
  	pass

  return False

def main():
  with open(sys.argv[1], 'r') as dotcom_names:
    for name in dotcom_names:
      name = name.strip()
      try:
        resolver.query(name, 'NS')
        print("[+] %s is taken" % name)
      except Exception as e:
        print("[+] %s might be available (%s)" % (name, e))
        if is_available(name):
          print("[!] \033[92m%s is available\033[0m" % name)
          with open('available_names.txt', 'a') as f:
            f.write("%s\n" % name)

if __name__ == '__main__':
  main()