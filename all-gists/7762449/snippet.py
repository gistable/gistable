import requests

API_KEY = 'YOUR_API_KEY'
BASE_URL = 'http://social.repustate.com/%(api_key)s/%(call)s.json'

# Create a new data source.
kwargs = {'api_key':API_KEY, 'call':'add-datasource'}
response = requests.post(BASE_URL % kwargs, {'name':'Rob Ford', 'language':'en', 'niche':'general'})
datasource_id = response.json()['datasource_id']

# Add a monitoring rule to our newly created data source.
kwargs['call'] = 'add-rule'
post_data = { 
    'datasource_id':datasource_id,
    'source_type':'twitter-all',
    'query':'"Rob Ford" OR "Mayor Ford" OR "#RoFo" OR Ford',
    # Restrict to only those tweets that contain geo information.
    'has_geo':1
}
response = requests.post(BASE_URL % kwargs, post_data