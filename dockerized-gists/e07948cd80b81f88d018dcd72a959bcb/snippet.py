# -*- coding: utf-8 -*-
import threading
import tweepy
import datetime
import sys
import urllib
import urllib2
import json
import random
import time

url = "https://itunes.apple.com/search?term=pokemon+go&country=fr&media=software&entity=software&lang=fr_fr"

auth = tweepy.OAuthHandler(OAUTH_KEY, OAUTH_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

messages = [
    "OUI.. Nan j'déconne. Nope.",
    "Non.",
    "Nope.",
    "OUI. Oh attendez. Je voulais dire \"en français\", pas \"en France\".",
    "J'ai posé la question  Niantic et ils m'ont répondu: \"Attendez, c'est quoi la France ? Ca se mange ?\"",
    "Nope, mais une source sûre a dit qu'il devrait sortir dans les prochaines 24h. J'ai lu ça il y a 48h.",
    "Non. Demandez à @fhollande et @manuelvalls s'ils ont quelque chose à voir avec ça.",
    "Non. Peut-être avant 2017",
    "Non. J'espère l'avoir avant Half Life 3.",
    "Lord Helix m'a dit que non.",
    "Négatif.",
    "Pokémon NO",
    "Vous aviez cru que j'allais dire oui hein ? Eh ben non.",
    "OUI.. Ah attendez, on me dit dans l'oreillette que la Suisse ne fait pas partie de la France.",
    "Super NON All-Stars Battle Royale at the Olympic Games HD Remix & Knuckles.",
    "BREAKING NEWS: Non.",
    "Nope.avi",
    "OUI : http://bit.ly/IqT6zt\n\nAttendez une minute... Non.",
    "Réponse courte: Non\nRéponse longue: Noooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooon",
    "Nein.",
    "Toujours pas.",
    "Pouce Rouge.",
    "MY BODY IS READY ! Mais le jeu ne l'est pas.",
    "3 lettres: Mot employé pour exprimer l'idée de négation. Antonyme de \"Oui\"",
    "N\no\nn\n."
    ]

out = False
last = -1

def log(text):
    print str(datetime.datetime.now().time().isoformat()) + ": " + str(text)

# On construit le tweet et on le balance
def tweet():
    if out:
        text = "OUI !\nPokemon GO est ENFIN disponible en France !\nTéléchargement iOS: http://itunes.apple.com/fr/app/pokemon-go/id109345?mt=8\nTéléchargement Android: https://play.google.com/store/apps/details?id=com.nianticlabs.pokemongo"
    else:
        now = datetime.datetime.now()
        text = "[{:02d}/{:02d} - {:02d}:{:02d}]\n".format(now.day, now.month, now.hour, now.minute) + messages[random.randint(0, len(messages)-1)]
    global api
    api.update_status(text)
    log(str("Tweeted:\n" + text + "\n"))

# Checks des status
def execute():
    global last
    log("Program started !\n")
    while True:
        now = datetime.datetime.now()
        if now.hour != last and now.minute == 0:
            try:
                r = urllib2.urlopen(url)
                root = json.loads(r.read())
                
                for data in root["results"]:
                    if u'Niantic, Inc.' in data[u'sellerName']:
                        log("OMG IT'S OUT !!!")
                        global out
                        out = True
                        tweet()
                        r.close()
                        sys.exit()

                log("Still not out...")
                tweet()
                r.close()
                
                last = now.hour
            except Exception, e:
                log("EXCEPTION: " + str(e))
                try:
                    r
                except NameError:
                    None
                else:
                    r.close()
        else:
            log("Now sleeping for " + str((59-now.minute)*60 + 30) + "s\n")
            time.sleep((59-now.minute)*60 + 30)
                    
        
execute()