import base64
import httplib
import threading
import urllib

import tweepy

CONVORE_BOT_USERNAME = ''
CONVORE_BOT_PASSWORD = ''
CONVORE_TOPIC_ID = '7612'

TWITTER_USERNAME = ''
TWITTER_PASSWORD = ''

TRACKING_KEYWORDS = ['python', 'pycon']


class StreamWatchListener(tweepy.StreamListener):
    
    def __init__(self, *args, **kwargs):
        username = kwargs.pop('username')
        password = kwargs.pop('password')
        topic_id = kwargs.pop('topic_id')
        super(StreamWatchListener, self).__init__(*args, **kwargs)
        encoded = base64.encodestring('%s:%s' % (username, password)).strip()
        self._convore_headers = {
            'Authorization': 'Basic %s' % (encoded,),
        }
        self._convore_url = '/api/topics/%s/messages/create.json' % (topic_id,)
    
    def _post_to_convore(self, status):
        message = '%s: %s' % (
            status.author.screen_name.encode('utf-8'),
            status.text.encode('utf-8'),
        )
        body = urllib.urlencode({'message': message})
        conn = httplib.HTTPSConnection('convore.com')
        conn.request('POST', self._convore_url, body, self._convore_headers)
        response = conn.getresponse()
        data = response.read()
    
    def on_status(self, status):
        threading.Thread(target=self._post_to_convore, args=[status]).start()
    
    def on_error(self, status_code):
        print 'An error has occured! Status code = %s' % status_code
        return True  # keep stream alive

    def on_timeout(self):
        print 'Snoozing Zzzzzz'


def main():
    listener = StreamWatchListener(
        username=CONVORE_BOT_USERNAME,
        password=CONVORE_BOT_PASSWORD,
        topic_id=CONVORE_TOPIC_ID,
    )
    stream = tweepy.Stream(
        TWITTER_USERNAME,
        TWITTER_PASSWORD,
        listener,
        timeout=None
    )
    #stream.sample()
    stream.filter(None, TRACKING_KEYWORDS)

if __name__ == '__main__':
    main()