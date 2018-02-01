#!/usr/bin/python

from urllib import quote_plus
from sys import stdin
from subprocess import call
import requests
import xml.etree.ElementTree as ET

appID = 'XXXXXX-YYYYYYYYYY'  # Placeholder. You'll need to get an ID from http://products.wolframalpha.com/api/

def get_plaintext_query(latex):    
  r = requests.get('http://api.wolframalpha.com/v2/query?input=%s&appid=%s' % (quote_plus(latex), appID))
  root = ET.fromstring(r.text.encode('utf8'))

  for pod in root:
    if pod.attrib.get('title', '') in ['Decimal approximation', 'Definite integral', 'Decimal form', 'Result']:
      subpod = pod.find('subpod')
      result = subpod.find('plaintext').text

      if pod.attrib.get('title', '') == 'Definite integral':
        return result.split('~~')[1]
      else:
        return result

if __name__ == '__main__':
  latex = stdin.read()
  alphaURL = "http://www.wolframalpha.com/input/?i=%s" % quote_plus(latex)
  print latex + ' = ' + get_plaintext_query(latex)
  call(['open', alphaURL])



