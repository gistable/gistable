import urllib,hmac,time,hashlib,base64,httplib,sys,json,urlparse

## This is just a simple example that is self contained. 
## You will need to modified it to make it work
##
## creds - need to be filled out
## blognmae - needs to be defined
##
## reads in image files from the command line and posts to your blog

class TumblrAPI:
    def __init__(self, cred):
        self.consumer_key = cred['consumer_key']
        self.secret_key = cred['secret_key'] + '&'
        self.oauth_token_secret= cred['oauth_token_secret']
        self.oauth_token = cred['oauth_token']

    def parse(self,url):
        p = urlparse.urlparse(url)
        return (p.netloc,p.netloc,p.path) 

    def oauth_sig(self,method,uri,params):
        s = method + '&'+ urllib.quote(uri).replace('/','%2F')+ '&' + '%26'.join([urllib.quote(k) +'%3D'+ urllib.quote(params[k]).replace('/','%2F') for k in sorted(params.keys())])
 25             '%26'.join([urllib.quote(k) +'%3D' + urllib.quote(params[k]).replace('/','%2F') for k in sorted(params.keys())])
        s = s.replace('%257E','~')
        return base64.encodestring(hmac.new(self.secret_key + self.oauth_token_secret,s,hashlib.sha1).digest()).strip()

    def oauth_gen(self,method,url,iparams,headers):
        params = dict([(x[0], urllib.quote(str(x[1])).replace('/','%2F')) for x in iparams.iteritems()]) 
        params['oauth_consumer_key'] = self.consumer_key
        params['oauth_nonce'] = str(time.time())[::-1]
        params['oauth_signature_method'] = 'HMAC-SHA1'
        params['oauth_timestamp'] = str(int(time.time()))
        params['oauth_version'] = '1.0'
        params['oauth_token']= self.oauth_token
        params['oauth_signature'] = self.oauth_sig(method,'http://'+headers['Host'] + url, params)
        headers['Authorization' ] =  'OAuth ' + ',  '.join(['%s="%s"' %(k,v) for k,v in params.iteritems() if 'oauth' in k ])
    def _postOAuth(self,url,params={}):
        (machine,host,uri) = self.parse(url)
        headers= {'Host': host,"Content-type": 'application/x-www-form-urlencoded'}
        self.oauth_gen('POST',uri,params,headers)
        conn = httplib.HTTPConnection(machine)
        conn.request('POST',uri,urllib.urlencode(params).replace('/','%2F'),headers);
        return conn.getresponse()

    def createPost(self,id,params={}):
        url = 'http://api.tumblr.com/v2/blog/%s/post' %id 
        return self._resp(self._postOAuth(url,params),201);

    def _resp(self,resp,code=200):
        if resp.status != code: 
            raise Exception('response code is %d - %s' % (resp.status,resp.read()));
        return json.loads(resp.read())['response']


cred = { "consumer_key" : 'consumer-key-scret',
        'secret_key' : 'secret-key',
        'oauth_token_secret' : 'oauth-token-secret',
        'oauth_token' :  'oauth-token'}
blogname = 'awesome-blog-name'

api = TumblrAPI(cred)

params = {}
params['type'] = 'photo'
for x in range(1,len(sys.argv)):
    params['data[%d]' % (x-1) ] = file(sys.argv[x]).read()
print api.createPost(blogname,params);