import os, requests, re
from htmlentitydefs import name2codepoint
from simplejson import loads, dumps

spauth = None

def unescape(s):
	name2codepoint['#39'] = 39
	return re.sub('&(%s);' % '|'.join(name2codepoint),
			lambda m: unichr(name2codepoint[m.group(1)]), s)

def generate_saml(options):
	# SAML.xml from https://github.com/lstak/node-sharepoint
	content = '<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing" xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"><s:Header><a:Action s:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/02/trust/RST/Issue</a:Action><a:ReplyTo><a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address></a:ReplyTo><a:To s:mustUnderstand="1">https://login.microsoftonline.com/extSTS.srf</a:To><o:Security s:mustUnderstand="1" xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"><o:UsernameToken><o:Username>[username]</o:Username><o:Password>[password]</o:Password></o:UsernameToken></o:Security></s:Header><s:Body><t:RequestSecurityToken xmlns:t="http://schemas.xmlsoap.org/ws/2005/02/trust"><wsp:AppliesTo xmlns:wsp="http://schemas.xmlsoap.org/ws/2004/09/policy"><a:EndpointReference><a:Address>[endpoint]</a:Address></a:EndpointReference></wsp:AppliesTo><t:KeyType>http://schemas.xmlsoap.org/ws/2005/05/identity/NoProofKey</t:KeyType><t:RequestType>http://schemas.xmlsoap.org/ws/2005/02/trust/Issue</t:RequestType><t:TokenType>urn:oasis:names:tc:SAML:1.0:assertion</t:TokenType></t:RequestSecurityToken></s:Body></s:Envelope>'
	for k in options.keys():
		content = content.replace('['+k+']', options[k])
	return content
	
def request_token(options):
	saml = generate_saml(options)
	result = requests.post('https://login.microsoftonline.com/extSTS.srf', data=saml)
	return unescape(result.text.split('<wsse:BinarySecurityToken Id="Compact0">')[1].split('</wsse:BinarySecurityToken>')[0])

def get(url):
	global spauth
	return requests.get(url, headers={'Cookie':spauth, 'Accept':'application/json'})

opts = {
	'username' : 'user@yourcompany.com',
	'password' : 'password',
	'endpoint':'https://yourcompany.sharepoint.com/_forms/default.aspx?wa=wsignin1.0'
}

# First grab our token from https://login.microsoftonline.com/extSTS.srf
token = request_token(opts)

# Then use that token to authenticate on our site.
result = requests.post(opts['endpoint'], token)

# For some reason, the requests module throws "s around each cookie, which messes up MSOnline's auth.
spauth = 'FedAuth=' + result.cookies['FedAuth'] + '; rtFa=' + result.cookies['rtFa']

# Lastly, let's test our authentication by grabbing some list data.
result = get('https://yourcompany.sharepoint.com/_vti_bin/ListData.svc/')
root = loads(result.text.encode('utf-8'))
import pprint
pprint.pprint(root)