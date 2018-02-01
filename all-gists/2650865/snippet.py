import time
import redis
import urllib
import threading
import simplejson

class Generator(threading.Thread):
    def __init__(self, generator, output_channel, _redis=None):
        threading.Thread.__init__(self)
        self.generator = generator
        self.output_channel = output_channel
        self.active = True
        
        if not _redis:
            self.redis = redis.Redis()
        else:
            self.redis = _redis
    
    def run(self):
        while self.active:
            data = self.generator.next()
            json = simplejson.dumps(data)
            self.redis.publish(self.output_channel, json)

class Actor(threading.Thread):
    def __init__(self, func, _redis=None, output_channel=None, input_channel='default'):
        threading.Thread.__init__(self)
        self.func = func
        
        if not _redis:
            self.redis = redis.Redis()
        else:
            self.redis = _redis
        
        self.pubsub = self.redis.pubsub()
        self.input_channel = input_channel
        self.output_channel = output_channel
        self.pubsub.subscribe(['main', input_channel])
    
    def run(self):
        for item in self.pubsub.listen():
            if item['type'] == 'message':
                if item['channel'] == self.input_channel:
                    data = simplejson.loads(item['data'])
                    temp = self.func(data)
                    if self.output_channel:
                        self.redis.publish(self.output_channel, simplejson.dumps(temp))
                elif item['channel'] == 'main':
                    if item['data'] == ''.join(["KILL:", hash(self)]):
                        break

# result_type can be mixed, recent or popular
# TODO: More error checking.
def twitter_public_search(query, wait=20, result_type='mixed'):
    max_id_str = None
    while True:
        try:
            if not max_id_str:
                params = urllib.urlencode({'q':query, 'result_type':result_type})
            else:
                params = urllib.urlencode({'q':query, 'result_type':result_type, 'since_id':max_id_str})
            
            search = urllib.urlopen(
                ''.join(["http://search.twitter.com/search.json?", params]))
            
            data = simplejson.loads(search.read())
            
            if data['max_id_str'] != '0':
                max_id_str = data['max_id_str']
            else:
                if len(data['results']) > 0:
                    max_id_str = data['results'][0]['id_str']
                else:
                    pass
            
            for item in data['results']:
                yield item
            
            time.sleep(wait)
        
        except KeyError:
            pass # retry the API call

def print_text(data):
    print data['text']
        
python_gen    = twitter_public_search("python", result_type='mixed')
search        = Generator(python_gen, 'twitter_search_python')
search_reader = Actor(print_text, input_channel='twitter_search_python')

search.start()
search_reader.start()