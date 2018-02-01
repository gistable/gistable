import requests
url = 'http://c.docverter.com/convert'
filename = 'curriculum-vita.md'
print 'Sending request to Docverter for file', filename
r = requests.post(url, data={'to':'pdf','from':'markdown'},files={'input_files[]':open(filename,'rb')})
if r.ok:
  outname = '.'.join(filename.split('.')[:-1])
  fout = open(outname, 'wb')
  fout.write(r.content)
  fout.close()
  print 'Output written to', outname
else:
  print 'Request failed:', r.status_code