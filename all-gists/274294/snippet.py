import urllib, json

class SABnzbd(object):
    """
    Usage:
    >>> from sabnzbd import SABnzbd
    >>> s = SABnzbd('sakar.local', 8080, '4488f2881b90d7753bef8fb9e1bc56b3')
    >>> s.pause() # Pauses the downloads
    >>> s.shutdown() # Shut's down SABnzbd+
    """
    
    def __init__(self, host, port=8080, key=''):
        self.host = host
        self.port = port
        self.key = key
    
    def request(self, mode, output=False, **kwargs):
        kwargs['apikey'] = self.key
        kwargs['mode'] = mode
        
        if output:
            kwargs['output'] = 'json'
        
        url = 'http://%s:%s/sabnzbd/api?%s' % (
            self.host,
            self.port,
            urllib.urlencode(kwargs)
            #'&'.join(['%s=%s' % (kwarg, kwargs[kwarg]) for kwarg in kwargs])
        )
        print url
        result = urllib.urlopen(url).read()
        
        if output:
            try:
                return json.JSONDecoder().decode(result)
            except ValueError:
                return {}
        
        return result
    
    def pause(self):
        self.request('pause')
    
    def resume(self):
        self.request('resume')
    
    def shutdown(self):
        self.request('shutdown')
    
    def status(self, advanced=False):
        if advanced:
            return self.request('status', True)
        else:
            return self.request('qstatus', True)
    
    def limit(self):
        try:
            return self.status(advanced=True)['limit']
        except:
            return
    
    def setLimit(self, value=0):
        self.request('config', name='speedlimit', value=value)
