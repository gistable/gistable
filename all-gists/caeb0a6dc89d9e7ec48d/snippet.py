#put the code in a python tag
#add a user data button to the tag

import c4d

#user data button
def message(id, data):
    if id == 17: 
        print "UserData-ID: ", data["descid"][1].id

def main():
    pass