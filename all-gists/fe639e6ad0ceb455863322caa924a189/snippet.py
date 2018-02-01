
from akamai_token_v2 import *

  corsHeaders = {

                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,x-requested-with',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,GET,OPTIONS'
              }
   
   // Called from an infrastructure like AWS Lambda or Python Flask
   
   def SignUrl(self):
        print "[*] SignUrl"
        stream  = self.messageBody.get('stream','')
        url     = self.config.get('SignUrl').get('url')
        key     = self.config.get('SignUrl').get('tokenKey')
        acl     = self.config.get('SignUrl').get('acl')
        windowSeconds = int(self.config.get('SignUrl').get('windowSeconds', 300))

        userAgent = self.headers.get('User-Agent',None)
        if not userAgent:
            userAgent = self.messageBody.get('UserAgent','Unknown')

        generator = AkamaiToken(window_seconds=windowSeconds,
                                key=key,
                                acl=acl)

        print "Salt: {}".format(userAgent)
        new_token = generator.generateToken()
        print new_token

        signedUrl = "{}?{}".format(url,new_token)

        body = {}
        body['salt'] = userAgent
        body['window'] = windowSeconds
        body['acl'] = acl
        body['url'] = signedUrl

        if stream == 'show':
            response = {}
            response['isBase64Encoded'] = False
            response['statusCode'] = 200
            response['body'] = dump_json(body)
            response['headers'] = corsHeaders
            return response

        response = {}
        rh = corsHeaders.copy()
        rh['location'] = signedUrl
        response['isBase64Encoded'] = False
        response['statusCode'] = 302
        response['body'] = dump_json({'location': signedUrl })
        response['headers'] = rh
        return response
