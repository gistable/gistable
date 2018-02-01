import urllib2, urllib
import logging

def send_mail_sendgrid(from, to, subject, body):
  base_url = 'https://sendgrid.com/api/mail.send.json'
  params = {
    'api_user': 'you@you.com',
    'api_key': 'yourpassword',
    'from': from,
    'to': to,
    'subject':  subject,
    'text': body
    }
  encoded_params = urllib.urlencode(params)
  url = '%s?%s' % (base_url, encoded_params)
  try:
    response = json.loads(urllib2.urlopen(url).read())
    if response['message'] == 'error':
      logging.info('Error sending message: %s' % errors.join(',')) 
  except urllib2.HTTPError, e:
    logging.info('Error sending message: %s, %s' % (e.code, e.read()))
