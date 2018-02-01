import requests
import json
from os import makedirs
from os.path import join, exists
from copy import copy
import requests
LIST_ENDPOINT='http://api.viewers-guide.hbo.com/service/charactersList'
FEATURED_ENDPOINT='http://api.viewers-guide.hbo.com/service/charactersFeatured'
DETAIL_ENDPOINT='http://api.viewers-guide.hbo.com/service/characterDetails'
DEFAULT_PARAMS = {'lang': 1}
MAX_EPISODE = 54
DATA_DIR = 'mydata'


for i in range(MAX_EPISODE):
    print("Episode", i)
    ep_params = copy(DEFAULT_PARAMS)
    ep_params['episode_id'] = i
    listresp = requests.get(LIST_ENDPOINT, ep_params)
    characterslist = listresp.json()
    if type(characterslist) is not list:
        print("Error:", listdata)
    else:
        epdir = join(DATA_DIR, 'episodes', str(i))
        makedirs(epdir, exist_ok=True)
        fname = join(epdir, 'charactersList.json')
        with open(fname, 'w') as wf:
            json.dump(characterslist, wf, indent=4)

        # get featured
        featresp = requests.get(FEATURED_ENDPOINT, ep_params)
        fname = join(epdir, 'charactersFeatured.json')
        with open(fname, 'w') as wf:
            json.dump(featresp.json(), wf, indent=4)


        chardir = join(epdir, 'characters')
        makedirs(chardir, exist_ok=True)
        for ch in characterslist:
            # fetch details on characters
            char_params = copy(ep_params)
            char_params['id'] = ch['id']
            print("Character", ch['id'], ch['firstname'], ch['lastname'])
            charresp = requests.get(DETAIL_ENDPOINT, char_params)
            print(charresp.url)
            fname = join(chardir, str(ch['id']) + '.json')
            with open(fname, 'w') as wf:
                json.dump(charresp.json(), wf, indent=4)

