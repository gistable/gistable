#actions to run on cron job
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from datetime import datetime
import simplejson as json
import urllib, urllib2, time
from hotspot.twitterklout.models import Tweet, Tweeter, Hashtag, Event, Location
#from django.db import models

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('--long', '-l', dest='long',
                help='Help for the long options'),
        )
    help = 'this is an automated script (use Cron) to collect data'
    
    #self.can_import_settings = True
    
    
    #pullDataFromTwitter
    def handle(self, **options):
        print 'oh hai wrld'
        
        events = Event
        querySet = events.objects.all()
        
        for events in querySet:
            self.pullTweets(events)
        
        
        #pullDataFromTwitter(Event.objects.filter(isActive = True))
        
    def pullTweets(self, obj):
        #print obj.name
        
        if obj.isActive() == True:
        
            url = 'http://search.twitter.com/search.json?q=%23' + obj.Hashtag.tag
            print obj.name
            
            import twitter
            api = twitter.Api()
        
            try:    
                #req = urllib2.Request(url)
                
                #response = urllib2.urlopen(req)
                #the_page = response.read() 
                #print the_page
                
                #loadedJson = json.loads(the_page)
                
                #loadedJson = json.loads(response.read())
                
                results = api.GetSearch(term=obj.Hashtag.tag)
                
                #print results[0].text
                
                
                flag = 0  
                while (results[flag].id != obj.Hashtag.lastStatusID) and (flag !=10):
                    print results[flag].text
                    print results[flag].user.screen_name
                    newTweeter = Tweeter(username=results[flag].user.screen_name)
                    
                    users = Tweeter
                    userquerySet = Tweeter.objects.all()
                    userTest = False
                    
                    for user in userquerySet:
	                    if user.username == results[flag].user.screen_name:
	                    	userTest=True
	
	                    if userTest == True:
	                        newTweeter = Tweeter(username=results[flag].user.screen_name)
	                        newTweeter.save()
	                    
	                    	newTweet = Tweet(content=results[flag].text, Tweeter=user)
	                    	
	                    	newTweet.save()
	                    	
	                    	break
	                    	
                    flag = flag + 1
                    
                #obj.Hashtag.lastStatusID.save(results[0].id)
                #obj.Hashtag.lastStatusID.save()
                
                
                     
                        
                        
                #print self.sentiment
            
            except Exception, detail: 
                print "Err ", detail 
       
       
       
    
    
