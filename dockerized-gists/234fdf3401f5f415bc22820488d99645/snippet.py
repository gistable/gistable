import json, urllib2, random

def getPacks():
    # Make an array mapping pack_code to full name.
    packCodeToName = {}
    packsJSON = urllib2.urlopen("https://netrunnerdb.com/api/2.0/public/packs")
    packs = json.loads(packsJSON.read().decode("utf-8"))["data"]
    for pack in packs:
        packCodeToName[pack["code"]] = pack["name"]
    return packCodeToName

def getFactions():
    # Make an array mapping faction_code to faction.
    factionCodeToName = {}
    factionsJSON = urllib2.urlopen("https://netrunnerdb.com/api/2.0/public/factions")
    factions = json.loads(factionsJSON.read().decode("utf-8"))["data"]
    for f in factions:
        factionCodeToName[f["code"]] = f["name"]
    return factionCodeToName

def getTypes():
    # Make an array mapping type_code to type.
    typeCodeToName = {}
    typesJSON = urllib2.urlopen("https://netrunnerdb.com/api/2.0/public/types")
    types = json.loads(typesJSON.read().decode("utf-8"))["data"]
    for t in types:
        typeCodeToName[t["code"]] = t["name"]
    return typeCodeToName

def getCards(packCodeToName, factionCodeToName, typeCodeToName, packs=None):
    # Returns an array of all card names in given packs.
    cardsJSON = urllib2.urlopen("https://netrunnerdb.com/api/2.0/public/cards")
    cards = json.loads(cardsJSON.read().decode("utf-8"))["data"]
    if packs != None:
        cards = [card for card in cards if card["pack_code"] in packs]
    return [card["title"] + " from " + packCodeToName[card["pack_code"]] + " which is a " + factionCodeToName[card["faction_code"]] + " " + typeCodeToName[card["type_code"]] + "." for card in cards]

def askToContinue():
    print ""
    redo = True
    newCards = True
    while redo:
        redo = False
        continueInput = raw_input("Pick more cards? (y/n) ").capitalize()
        if continueInput == "N":
            newCards = False
        elif continueInput != "Y":
            redo = True
            print "Type y or n, please."
    print ""
    return newCards

def pickCards(packs, numberOfCards):
    pctn = getPacks()
    fctn = getFactions()
    tctn = getTypes()
    cards = getCards(pctn, fctn, tctn, packs)
    newCards = True
    while newCards:
        chosen = []
        while len(chosen) < numberOfCards:
            rand = int(random.random() * len(cards))
            if not rand in chosen:
                chosen.append(rand)
        for card in chosen:
            print cards[card]
        newCards = askToContinue()

if __name__ == '__main__':
    pickCards(["core", "td"], 5) # pickCards(None, x) picks from the entire cardpool (aka hard mode)
