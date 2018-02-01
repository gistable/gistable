import urllib,hmac,time,hashlib,base64,httplib,sys,json,urlparse

## This is just a simple example that is self contained. 
## You will need to modified it to make it work
##
## creds - need to be filled out
## blognmae - needs to be defined
##
## reads in image files from the command line and posts to your blog
##
## Your example body will contain something like:
##
## data%5B0%5D= => data[0]=<start binary>
##
## So from here you can gather that it's data[0], data[1] and so on.
##
## This code works for single photos as well as multiple photos
##
## Code was tested usings Python 2.7, no guarantees it'll work for others.
## Usage:
##   python gistfilename.py example1.jpg [example2.jpg example3.jpg ...]
##
##

class TumblrAPI:
    def __init__(self, cred):
        self.consumer_key = cred['consumer_key']
        self.secret_key = cred['secret_key']
        self.oauth_token_secret= cred['oauth_token_secret']
        self.oauth_token = cred['oauth_token']

    def parse(self,url):
        p = urlparse.urlparse(url)
        return (p.netloc,p.netloc,p.path) 

    def oauth_sig(self,method,uri,params):
        """
        Creates the valid OAuth signature.
        """
        #eg: POST&http%3A%2F%2Fapi.tumblr.com%2Fv2%2Fblog%2Fexample.tumblr.com%2Fpost
        s = method + '&'+ urllib.quote(uri).replace('/','%2F')+ '&' + '%26'.join(
            #escapes all the key parameters, we then strip and url encode these guys
            [urllib.quote(k) +'%3D'+ urllib.quote(params[k]).replace('/','%2F') for k in sorted(params.keys())]
        )
        s = s.replace('%257E','~')
        return urllib.quote(base64.encodestring(hmac.new(self.secret_key + "&"+self.oauth_token_secret,s,hashlib.sha1).digest()).strip())

    def oauth_gen(self,method,url,iparams,headers):
        """
        Creates the oauth parameters we're going to need to sign the body
        """
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
        """
        Does the actual posting. Content-type is set as x-www-form-urlencoded
        Everything url-encoded and data is sent through the body of the request.
        """
        (machine,host,uri) = self.parse(url)
        headers= {'Host': host,"Content-type": 'application/x-www-form-urlencoded'}
        self.oauth_gen('POST',uri,params,headers)
        conn = httplib.HTTPConnection(machine)
        #URL Encode the paramers and  make sure and kill any trailing slashes.
        conn.request('POST',uri,urllib.urlencode(params).replace('/','%2F'),headers);
        return conn.getresponse()

    def createPost(self,id,params={}):
        url = 'http://api.tumblr.com/v2/blog/%s/post' %id 
        return self._resp(self._postOAuth(url,params),201);

    def _resp(self,resp,code=200):
        if resp.status != code: 
            raise Exception('response code is %d - %s' % (resp.status,resp.read()));
        return json.loads(resp.read())['response']


cred = { "consumer_key" : 'your-consumer-key',
        'secret_key' : 'your-consumer-secret',
        'oauth_token' : 'access-token',
        'oauth_token_secret' :  'access-token-secret'}
blogname = 'manurday.tumblr.com'

api = TumblrAPI(cred)

params = {}
params['type'] = 'photo'
for x in range(1,len(sys.argv)):
    params['data[%d]' % (x-1) ] = file(sys.argv[x]).read()
print api.createPost(blogname,params);
