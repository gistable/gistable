import cherrypy
import jwt
import urllib.parse, urllib.request
import json
 
SPSECRET = 'gpYucHkODHOv6JxZJ89Kihl9ncTiTrUCAbOaF1N6uJE='
 
cherrypy.config.update({'server.socket_port': 3005,
                        'server.ssl_module': 'builtin',
                        'server.ssl_certificate': 'cert.pem',
                        'server.ssl_private_key': 'privkey.pem'})
 
class GetAccessToken(object):
    def index(self, **kwargs):
        cl = cherrypy.request.body.params
        spapptoken = cl['SPAppToken']
        decodedtoken = jwt.decode(spapptoken, SPSECRET, verify=False)
        
        url = json.loads(decodedtoken['appctx'])['SecurityTokenServiceUri']
        values = {
            'grant_type': 'refresh_token',
            'client_id': decodedtoken['aud'].split('/')[0],
            'client_secret': SPSECRET,
            'refresh_token': decodedtoken['refreshtoken'],
            'resource': decodedtoken['appctxsender'].split('@')[0] + '/' + decodedtoken['aud'].split('/')[1].split('@')[0] + '@' + decodedtoken['appctxsender'].split('@')[1]
        }
        data = urllib.parse.urlencode(values)
        binarydata = data.encode('ascii')
        req = urllib.request.Request(url, binarydata)
        response = urllib.request.urlopen(req)
        page = response.read()
        
        return repr(page)
        
    index.exposed = True
 
cherrypy.quickstart(GetAccessToken())