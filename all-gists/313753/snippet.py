from google.appengine.api import urlfetch
from google.appengine.api import xmpp
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import xmpp_handlers

import base64
import feedparser
import logging
import urllib
import urlparse
import uuid


HUB_URL = 'http://superfeedr.com/hubbub'
HUB_CREDENTIALS = ('username', 'password')


class Subscription(db.Model):
  @property
  def url(self):
    return self.key().name()

  verify_token = db.StringProperty(required=True)  # Random verification token.


class Subscriber(db.Model):
  @property
  def subscription(self):
    return self.parent
  
  @property
  def address(self):
    return self.key().name()


def add_subscription(topic, recipient):
  created = False
  subscription = Subscription.get_by_key_name(topic)
  if not subscription:
    created = True
    subscription = Subscription(key_name=topic, verify_token=str(uuid.uuid4()))
  subscriber = Subscriber(key_name=recipient, parent=subscription)
  db.put([subscription, subscriber])
  return created, subscription, subscriber


def find_self_url(links):
  for link in links:
    if link.rel == 'self':
      return link.href
  return None

class XmppHandler(xmpp_handlers.CommandHandler):
  def send_subscription_request(self, subscription):
    subscribe_args = {
        'hub.callback': urlparse.urljoin(self.request.url, '/hubbub'),
        'hub.mode': 'subscribe',
        'hub.topic': subscription.url,
        'hub.verify': 'async',
        'hub.verify_token': subscription.verify_token,
    }

    headers = {}

    if HUB_CREDENTIALS:
      auth_string = "Basic " + base64.b64encode("%s:%s" % HUB_CREDENTIALS)
      headers['Authorization'] = auth_string

    response = urlfetch.fetch(HUB_URL, payload=urllib.urlencode(subscribe_args),
                              method=urlfetch.POST, headers=headers)


  def subscribe_command(self, message):
    if not message.arg.startswith("http"):
      message.reply("Subscription requests must consist of a URL to subscribe to")
      return

    created, subscription, subscriber = db.run_in_transaction(
        add_subscription,
        message.arg,  # URL to subscribe to
        message.sender,  # User who is subscribing
    )

    if created:
      self.send_subscription_request(subscription)
    
    message.reply("Subscription created!")


class CallbackHandler(webapp.RequestHandler):
  def get(self):
    if self.request.GET['hub.mode'] == 'unsubscribe':
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write(self.request.GET['hub.challenge'])
      return
      
    if self.request.GET['hub.mode'] != 'subscribe':
      self.error(400)
      return

    subscription = Subscription.get_by_key_name(self.request.GET['hub.topic'])
    if not subscription or subscription.verify_token != self.request.GET['hub.verify_token']:
      self.error(400)
      return

    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write(self.request.GET['hub.challenge'])

  def post(self):
    """Handles new content notifications."""
    feed = feedparser.parse(self.request.body)
    id = find_self_url(feed.feed.links)
    subscription = Subscription.get_by_key_name(id)
    subscriber_keys = Subscriber.all(keys_only=True).ancestor(subscription).fetch(1000)
    subscriber_addresses = [x.name() for x in subscriber_keys]
    if not subscription:
      logging.warn("Discarding update from unknown feed '%s'", id)
      return
    for entry in feed.entries:
      message = "%s (%s)" % (entry.title, entry.link)
      xmpp.send_message(subscriber_addresses, message)


application = webapp.WSGIApplication([
  ('/_ah/xmpp/message/chat/', XmppHandler),
  ('/(?:hubbub)', CallbackHandler),
], debug=False)


def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()