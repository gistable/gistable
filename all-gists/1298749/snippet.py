#!/usr/bin/env python                                                                                                                                                                
                                                                                                                                                                                     
import urllib                                                                                                                                                                        
import urlparse                                                                                                                                                                      
import oauth2 as oauth                                                                                                                                                               
                                                                                                                                                                                     
consumer_key="asdfsafdsafsdfsdafsafsdafsafdsafsafdsfasfsdafdas"                                                                                                                      
consumer_secret="asdfsafdsafsdfsdafsdafsdfsdfasdfsdaf"                                                                                                                               
access_token_url = 'https://www.tumblr.com/oauth/access_token'                                                                                                                       
                                                                                                                                                                                     
consumer = oauth.Consumer(consumer_key, consumer_secret)                                                                                                                             
client = oauth.Client(consumer)                                                                                                                                                      
client.add_credentials("john@testingwoo.com","testingpassword")                                                                                                                      
client.authorizations                                                                                                                                                                
                                                                                                                                                                                     
params = {}                                                                                                                                                                          
params["x_auth_username"] = "john@testingwoo.com"                                                                                                                                    
params["x_auth_password"] = "testingpassword"                                                                                                                                        
params["x_auth_mode"] = 'client_auth'                                                                                                                                                
                                                                                                                                                                                     
client.set_signature_method = oauth.SignatureMethod_HMAC_SHA1()                                                                                                                      
resp, token = client.request(access_token_url, method="POST",body=urllib.urlencode(params))                                                                                          
                                                                                                                                                                                     
print resp                                                                                                                                                                           
                                                                                                                                                                                     
access_token = dict(urlparse.parse_qsl(token))                                                                                                                                       
                                                                                                                                                                                     
print access_token                                                                                                                                                                   
                                                                                                                                                                                     
access_token = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])                                                                                          
client = oauth.Client(consumer, access_token)                                                                                                                                        
print client.request("http://api.tumblr.com/v2/user/info", method="POST")    