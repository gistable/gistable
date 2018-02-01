import requests
import os

class BungieData(object):
    '''
    For the API calls below, no authentication is needed. You'll just need to have your Bungie API key exported in your bash profile
    and named as BUNGIE_API_KEY to run the script as-is.
    '''

    def __init__(self, api_key):
        '''
        api_key (str): The api key given to you by Bungie when you registered your app with them
        '''
        self.api_key = api_key

    def get_playerByTagName(self, gamertag):
        '''gamertag (str): The PSN gamertag a player uses on Destiny 2'''
        site_call = "https://bungie.net/Platform/Destiny2/SearchDestinyPlayer/2/" + gamertag
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_DestinyUserId(self, gamertag):
        '''gamertag (str): The PSN gamertag a player uses on Destiny 2'''
        info = self.get_playerByTagName(gamertag)
        return int(info[0]['membershipId'])

    def get_BungieUserId(self, membership_id):
        '''
        membership_id (int): the Destiny membership_id of a player (the id returned by get_DestinyUserId)
        Uses old Destiny endpoint for a PSN user to get the BUNGIE membershipId
        '''
        site_call = "https://bungie.net/Platform/User/GetMembershipsById/" + str(membership_id) + "/2/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return int(request.json()['Response']['bungieNetUser']['membershipId'])

    def get_DestinyUserProfile(self, membership_id, components=[100]):
        '''
        membership_id (int): the Destiny membership_id of a player (returned by get_DestinyUserId)
        components (list of ints): the type of info you want returned according the Bungie API docs.
          Defaults to 100: basic profile info ([100, 200] would also return more detailed info by Destiny character
        Uses new Destiny 2 endpoint for PSN player using the Destiny membershipId
        '''
        components = "?components=" + ','.join([str(c) for c in components])
        site_call = "https://bungie.net/Platform/Destiny2/2/Profile/" + str(membership_id) + "/" + components
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_postGameStats(self, game_id):
        '''game_id (int): Need to look further into this, but game_ids can be found'''
        site_call = "https://bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/" + str(game_id)
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_Manifest(self):
        site_call = "https://bungie.net/Platform/Destiny2/Manifest/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_PlayerStats(self, membership_id):
        site_call = "https://bungie.net/Platform/Destiny2/2/Account/" + str(membership_id) + "/Stats/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']

    def get_StatDefinitions(self):
        site_call = "https://bungie.net/Platform/Destiny2/Stats/Definition/"
        request = requests.get(site_call,
                                headers={"X-API-Key":self.api_key})
        return request.json()['Response']


if __name__ == '__main__':
    bungie = BungieData(api_key=os.environ["BUNGIE_API_KEY"]) # Never put your keys in code... export 'em!

    # Get Destiny MembershipId by PSN gamertag
    my_destiny_id = bungie.get_DestinyUserId("BalancedSeeker6")
    print("BalancedSeeker6's Destiny ID: {}".format(my_destiny_id))
    print("-----------------")

    # Get User's Profile info and more detailed Character info
    my_profile = bungie.get_DestinyUserProfile(my_destiny_id, components=[100,200])
    print("Destiny Profile Info by Charcter: \n{}".format(my_profile))
    print("-----------------")

    # Get a random single game's post carnage stats
    game_stats = bungie.get_postGameStats(100)
    print("Random Destiny 2 game's post carnage game stats: \n{}".format(game_stats))
