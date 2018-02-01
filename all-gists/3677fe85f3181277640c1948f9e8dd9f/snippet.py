# coding: utf-8

# Note to self: do proper authorization at: https://github.com/sarumont/py-trello/blob/master/trello/util.py

import sys
if sys.argv == [] or len(sys.argv) == 1:
    sys.exit()

clArgs = sys.argv[1].split(',')

if clArgs == [] or len(clArgs) != 4:
    sys.exit()

# Must pass in Trello API Key, Trello App Token, Trello boardId, and Trello username
appKey = clArgs[0]
appToken = clArgs[1]
boardId = clArgs[2]
userName = clArgs[3]

import platform

if platform.system() == 'Darwin':
    if platform.machine().startswith('iP'):
        # we're running on an iOS device
        import console
        import clipboard
        import webbrowser

import urllib2
import urllib
import json

# to properly encode unicode characters in JSON objects
def encode_obj(in_obj):
    def encode_list(in_list):
        out_list = []
        for el in in_list:
            out_list.append(encode_obj(el))
        return out_list
    def encode_dict(in_dict):
        out_dict = {}
        for k, v in in_dict.iteritems():
            out_dict[k] = encode_obj(v)
        return out_dict
    if isinstance(in_obj, unicode):
        return in_obj.encode('utf-8')
    elif isinstance(in_obj, list):
        return encode_list(in_obj)
    elif isinstance(in_obj, tuple):
        return tuple(encode_list(in_obj))
    elif isinstance(in_obj, dict):
        return encode_dict(in_obj)
	return in_obj

myCards = []

args = {
'fields': 'id',
'key': appKey,
'token': appToken
}

memberUrl = "https://api.trello.com/1/members/%s?%s" % (userName, urllib.urlencode((args)))

try:
    data = urllib2.urlopen(memberUrl)
except urllib2.HTTPError as inst:
    raise Exception("Key or Token incorrect")

member = json.loads(data.read())

args = {
'fields': 'id,name,cards',
'key': appKey,
'token': appToken,
'filter': 'open'
}

listsUrl = "https://api.trello.com/1/boards/%s/lists?%s" % (boardId, urllib.urlencode((args)))

try:
    data = urllib2.urlopen(listsUrl)
except urllib2.HTTPError as inst:
    raise Exception("Key or Token incorrect")

lists = json.loads(data.read())

args = {
'fields': 'all',
'key': appKey,
'token': appToken
}

# in case there are lists on the Trello board you don't care about - skipping lists can speed up parsing operations
listsToExclude = []

gen = (x for x in lists if x['name'] not in listsToExclude)
for li in gen:
    cardsUrl = "https://api.trello.com/1/lists/%s/cards?%s" % (li['id'], urllib.urlencode((args)))

    try:
        cardsData = urllib2.urlopen(cardsUrl)
    except urllib2.HTTPError as inst:
        raise Exception("Key or Token incorrect")

    cards = json.loads(cardsData.read())

    gen = (x for x in cards if member['id'] in x['idMembers'])

    for card in gen:
        myCards.append(card)

newline = '\n'
comma = ','
spaceHashtag = ' #'
spaceAtSign = ' @'
myTasks = []
myJsonTasks = []

for card in myCards:
    cardNum = card['idShort']
    cardName = card['name']
    cardLabels = card['labels']
    listId = card['idList']

    listGen = (x for x in lists if x['id'] == listId)
    listName = ''
    for li in listGen:
        listName = li['name']

    taskTitle = "Card #%s - %s" % (cardNum, cardName)

    labelNames = []
    labelNamesNoSpaces = []
    for label in cardLabels:
        labelName = label['name']
        labelNames.append(labelName)
        labelNamesNoSpaces.append(labelName.replace(" ","_"))

    hashtaglabels = spaceHashtag.join(labelNamesNoSpaces)
    atsignlabels = spaceAtSign.join(labelNamesNoSpaces)

    if hashtaglabels != "":
     # for Wunderlist
     hashtaglabels = '#' + hashtaglabels
     # for Todoist
    if atsignlabels != "":
     atsignlabels = '@' + atsignlabels

    taskData = {
    'Title': taskTitle,
    'shortUrl': card['shortUrl'],
    'desc': card['desc'],
    'idShort': cardNum,
    'labels': cardLabels,
    'pos': card['pos'],
    'name': cardName,
    'labelString': comma.join(labelNames),
    'labelStringHashtag': hashtaglabels,
    'labelStringAtSign': atsignlabels,
    'closed': card['closed'],
    'dateLastActivity': card['dateLastActivity'],
    'due': card['due'],
    'idList': listId,
    'ListName': listName,
    'subscribed': card['subscribed'],
    'url': card['url'],
    'FullData': card
    }

# Fields I've left out:
#   badges
#   checkItemStates
#   descData
#   idAttachmentCover
#   idBoard
#   idChecklists
#   idLabels
#   idMembers
#   idMembersVoted
#   manualCoverAttachment
#   shortLink
#   email

    myTasks.append(taskData)
    myJsonTasks.append(urllib.urlencode(taskData).replace('+','%20'))

if platform.system() == 'Darwin':
    if platform.machine().startswith('iP'):
        clipboard.set(newline.join(myJsonTasks))
        webbrowser.open('workflow://')
else:
    # this is for me to dump the data into C#
    jsonTasks = json.dumps(myTasks)
    print jsonTasks
