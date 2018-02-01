import time
import json
import urllib2
import matplotlib.pyplot as plt

# change this to something big, hundreds or thousands
n_users = 10

chess960 = []
blitz = []
kingOfTheHill = []
threeCheck = []
antichess = []
bullet = []
correspondence = []
puzzle = []
atomic = []
opening = []
classical = []

# get a list of users
users_json = urllib2.urlopen(
    'http://en.lichess.org/api/user?nb=' + str(n_users)).read()
users = json.loads(users_json)

for i, user in enumerate(users['list']):
    print 'Processing user', (i + 1)

    # send request for individual user
    user_json = urllib2.urlopen(
        "http://en.lichess.org/api/user/" + user['username']).read()
    user_perfs = json.loads(user_json)['perfs']

    # gather data
    chess960.append(int(user_perfs['chess960']['rating']))
    blitz.append(int(user_perfs['blitz']['rating']))
    kingOfTheHill.append(int(user_perfs['kingOfTheHill']['rating']))
    threeCheck.append(int(user_perfs['threeCheck']['rating']))
    antichess.append(int(user_perfs['antichess']['rating']))
    bullet.append(int(user_perfs['bullet']['rating']))
    correspondence.append(int(user_perfs['correspondence']['rating']))
    puzzle.append(int(user_perfs['puzzle']['rating']))
    atomic.append(int(user_perfs['atomic']['rating']))
    opening.append(int(user_perfs['opening']['rating']))
    classical.append(int(user_perfs['classical']['rating']))

    # dont hammer the server - sleep for 1 second between requests
    time.sleep(1)


# If you're running this for real, you should probably break here,
# save the data and load it back up again to do the analysis.
# You don't want to have to wait around every time you try a different graph

# plot a histogram for the player blitz ratings
# replace with whatever game you want to look at
plt.hist(blitz)
plt.show()
