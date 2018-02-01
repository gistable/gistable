import requests

scraper_urls = [
  'http://foo.net/TESTDIR/TEST.pdf',
  'http://foo.net/TESTDIR/TEST2.pdf'
  ]
p_session = requests.session()

for surl in scraper_urls:
    content = p_session.get(surl).content
    fname = surl.split('/')[-1]
    with open(fname, 'w') as f:
        f.write(content)