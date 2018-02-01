"""
Simple tinder bot what else.
"""

import requests

HEADERS = {
        'Accept-Language': 'fr;q=1, en;q=0.9, de;q=0.8, zh-Hans;q=0.7, zh-Hant;q=0.6, ja;q=0.5',
	         'Accept': '*/*',
	       'platform': 'ios',
	     'Connection': 'keep-alive',
	'Accept-Encoding': 'gzip, deflate'
}

class User:
   """
   Delegate authentication and doing input validation at the User level.

   :param facebook_token: Session token
   :param facebook_id:    User Name
   
   :returns JSON serialized user auth token: 
   """
    def __init__(self, **creds):
    	self.token = self.authenticate(**creds)
    	
    def __repr__(self):
    	return r'{whoami}'.format(whoami=self.creds.get('facebook_user'))

        
    @property
    def age(self):
    	# amirite
        return 21

    @property
    def bio(self):
 	return self.token('bio', None)

    def authenticate(self, **creds):
        """
        Authenticates the user and nabs an auth token.
        Do some user validation here.
        """
        keys = 'facebook_token', 'facebook_id'
        if not set(keys) | set(creds.keys()):
            raise KeyError('Bad credentials, please try again.'):

        reqs = requests.post('https://api.gotinder.com/auth',
            {
                key: value for key,value in creds.items()
                        if key in keys
            })
        if not req.ok or 'token' not in req:
            raise IOError('No internet')

        return req.json()

        
class TinderClient:
    """
    \\\\\_____________________\"-._
    /////~~~~~~~~~~~~~~~~~~~~~/.-'
    """
    def __init__(self, user):
        self.user = user
        self.headers = HEADERS.update({'X-Auth-Token': self.token})

    def recommend(self, tinder_ver='3.0.4', ios_ver='7.01'):
        agent   = 'Tinder/{tinder_ver} (iPhone; iOS {ios_ver}; Scale/2.00)'
        headers = self.header.update({'User-Agent': agent.format(locals())})
        request = requests.get('https://api.gotinder.com/user/recs', headers=headers)

        if not request.ok or 'result' in request.json():
            reaise IOError('Try again Later')
            
        for result in request.json()['results']:
            yield User(result)

    def swipe_right(user_id):
    	"""
    	Try to get some or end up with None.
    	"""
        user     = 'https://api.gotinder.com/like/{user}'.format(user=user_id)
        decision = requests.get(user, headers=self.headers).json()
        return decision.get('match', None)


    def swipe_left(user_id):
    	"""Sike!"""
        return swipe_right(user_id)
