#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, urllib2, json

RPC_URL = 'http://192.168.1.2/jsonrpc'

def pushStream(stream, rpc=RPC_URL):
    '''
    Push stream URL to XBMC jsonrpc api, XBMC play the streaming.
    '''
    data = {
        'jsonrpc': '2.0', 
        'method': 'Player.Open',
        'params':{
            'item': {
                'file': stream
            }
        },
        'id': '1'
    }

    r = urllib2.Request(rpc)
    r.add_header('Content-type', 'application/json')
    r.add_data(json.dumps(data))

    response = urllib2.urlopen(r)
    msg = json.loads(response.read())
    if msg.get('error'):
        print "Failed to push %s to XBMC, Message: %s" % (stream, msg.get('error').get('message'))
    elif msg.get('result') == 'OK':
        print 'Success to push %s to XBMC.' % stream
    else:
        print 'Unknown message %s.' % msg
    
def getStream(url):
    '''
    Get xunlei streaming from download url.
    '''
    data = urllib.urlencode(dict(url=url))
    l = data.split('=')
    data = '='.join([urllib.quote(x) for x in l])
    r = 'http://vod.dychao.com/i/posturl1'
    response = urllib2.urlopen(r, data)
    re = response.read().strip()
    if 'null' in re:
        raise IOError('No response, check the url.')
    else:
        return urllib.unquote(re)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        url = getStream(sys.argv[1])
        pushStream(url)
    else:
        print 'Example: python player.py magnet:?xt=...'
