# Run this script using "share" or "unshare" as arguments:
# To share the Plex libraries:
#     python share_unshare_libraries.py share
# To unshare the Plex libraries:
#     python share_unshare_libraries.py unshare

import requests
import sys
from xml.dom import minidom

## EDIT THESE SETTINGS ###

PLEX_TOKEN = "ENTER_YOUR_PLEX_TOKEN_HERE"
SERVER_ID = "ENTER_YOUR_SERVER_ID_HERE"  # Example: https://i.imgur.com/EjaMTUk.png

# Get the User IDs and Library IDs from
# https://plex.tv/api/servers/SERVER_ID/shared_servers
# Example: https://i.imgur.com/yt26Uni.png
# Enter the User IDs and Library IDs in this format below:
#     {UserID1: [LibraryID1, LibraryID2],
#      UserID2: [LibraryID1, LibraryID2]}

USER_LIBRARIES = {1234567: [1234567, 1234567]}

## DO NOT EDIT BELOW ##

def share():
    headers = {"X-Plex-Token": PLEX_TOKEN,
               "Accept": "application/json"}
    url = "https://plex.tv/api/servers/" + SERVER_ID + "/shared_servers"
               
    for user_id, library_ids in USER_LIBRARIES.iteritems():
        payload = {"server_id": SERVER_ID,
                   "shared_server": {"library_section_ids": library_ids,
                                     "invited_id": user_id}
                   }
                   
        r = requests.post(url, headers=headers, json=payload)
        
        if r.status_code == 401:
            print "Invalid Plex token"
            return
            
        elif r.status_code == 400:
            print r.content
            return
    
        elif r.status_code == 200:
            print "Shared libraries with user %s" % str(user_id)
            return
    
    return
    
def unshare():
    headers = {"X-Plex-Token": PLEX_TOKEN,
               "Accept": "application/json"}
               
    url = "https://plex.tv/api/servers/" + SERVER_ID + "/shared_servers"
    r = requests.get(url, headers=headers)

    if r.status_code == 401:
        print "Invalid Plex token"
        return
        
    elif r.status_code == 400:
        print r.content
        return

    elif r.status_code == 200:
        response_xml = minidom.parseString(r.content)
        MediaContainer = response_xml.getElementsByTagName("MediaContainer")[0]
        SharedServer = MediaContainer.getElementsByTagName("SharedServer")
        
        shared_servers = {int(s.getAttribute("userID")): int(s.getAttribute("id"))
                          for s in SharedServer}
        
        for user_id, library_ids in USER_LIBRARIES.iteritems():
            server_id = shared_servers.get(user_id)
            
            if server_id:
                url = "https://plex.tv/api/servers/" + SERVER_ID + "/shared_servers/" + str(server_id)
                r = requests.delete(url, headers=headers)
                
                if r.status_code == 200:
                    print "Unshared libraries with user %s" % str(user_id)
            
            else:
                print "No libraries shared with user %s" % str(user_id)
                    
    return
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'You must provide "share" or "unshare" as an argument'
        
    elif sys.argv[1] == "share":
        share()    
        
    elif sys.argv[1] == "unshare":
        unshare()