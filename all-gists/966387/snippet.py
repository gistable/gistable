from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from generic.models import Item, Profile
import urllib2
import twitter
import cjson

class Command(BaseCommand):
    help = 'Checks all #sociasell hashtags and sends messages'

    def handle(self, *args, **options):
        url = 'http://search.twitter.com/search.json?rpp=100&q=%%23%s' % settings.HASHTAG
        response = urllib2.urlopen(url).read()
        data = cjson.decode(response)

        api = twitter.Api(consumer_key=settings.TWITTER_CONSUMER_KEY, \
            consumer_secret=settings.TWITTER_CONSUMER_SECRET, \
            access_token_key=settings.TWITTER_ACCESS_TOKEN, \
            access_token_secret=settings.TWITTER_TOKEN_SECRET)
        
        for res in data.get('results', []):
            if Item.objects.filter(tweet_id=res['id']).count() == 0:
                ''' 
                New item, not processed yet, process please!
                '''
                user_id = res['from_user_id']
                item = Item(title=res['text'], tweet_id=res['id'], twittername=res['from_user'])
                item.save()
                msg = '@%s Use this link to create your online sociasell offer: http://sociasell.com/add/%d/' % (res['from_user'], item.id )
                print msg
                api.SetSource('sociasell.com')
                api.PostUpdate(msg)
