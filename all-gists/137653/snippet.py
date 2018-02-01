import html5lib
from html5lib import treebuilder

def parse_data(player_urls):
# Returns a dict of player data parse trees indexed by player name
    # Create a dict indexed by player names
    player_data=dict.fromkeys(player_urls.keys())
    # Download player profile data and parse using html5lib
    for name in player_urls.keys():
    # html5lib integrates the easy-to-use BeautifulSoup parse tree using the treebuilders library.
    # We will use this to parse the html
        parser=html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("beautifulsoup"))
        tree=parser.parse(urllib2.urlopen(player_urls[name]).read())
        # The data we are looking for is contained in a <p></p> tag, so we search for these tags
        data=tree.findAll("p")
        # By examining one of the HTML sources, we see that the exact data we need are in this range,
        # so we extract just what we want
        stats=data[2:5]
        # The data is stored in Unicode, so we must decode this before moving on.
        # We also know, from examining the HTML that the data sequence is:
        #   1. height
        #   2. weight
        #   3. dob
        #   4. college
        # So, we will now extract that data and place it in our storage dict
        data_temp=[]
        for i in stats:
        # All important data comes after a colon, so we split on it
            decoded=i.decode("utf-8")
            pieces=decoded.split(':')
            data_temp.append(pieces)
        # Create a dict 
        player_dict=dict.fromkeys(['height','weight','dob','college'])
        # Once split and stored in data_temp, we use our knowledge of the HTML structure to extract the correct data.
        # The remaining work is all string cleaning
        # Extract height
        height=string_cleaner_hw(data_temp[0][1])
        player_dict['height']=height
        # Extract weight
        weight=int(string_cleaner_hw(data_temp[0][2]))
        player_dict['weight']=weight
        # Extract DOB
        dob=string_cleaner_dob(data_temp[1][1])
        player_dict['dob']=dob
        # Extarct college
        college=string_cleaner_college(data_temp[2][1])
        player_dict['college']=college
        player_data[name]=player_dict
        
    return player_data
    
def string_cleaner_hw(data_string):
# Small helper function to do string cleaning on height and weight data
    data_string=data_string.strip()
    data_string=data_string.split('\n')[0]
    return data_string.split(' ')[0].encode()
    
def string_cleaner_dob(data_string):
# Small helper function to do string cleaning on DOB data
    data_string=data_string.strip()
    data_string=data_string.split('\t')[0]
    return data_string.split('\n')[0].encode()
            
def string_cleaner_college(data_string):
# Small helper function to do string cleaning on college data
    data_string=data_string.strip()
    return data_string.split('\n')[0].encode()

parsed_player_data=parse_data(player_urls)
print parsed_player_data