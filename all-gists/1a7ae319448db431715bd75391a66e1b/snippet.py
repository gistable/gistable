#! /usr/bin/python

import dota2api
from dota2api.src.exceptions import APIError, APITimeoutError
import csv
from multiprocessing import Pool
import time
import sys

def getMatchInfo( api, matchId ):
    for retries in range(3):
        try:
            match = api.get_match_details(match_id=matchId)
            break
        except APIError as e:
            print e.msg
            raise APIError('Getting match ' + str(matchId) + ' Failed')
        except Exception as e:
            print sys.exc_info()
            if retries == 2:
                raise APIError('Getting match ' + str(matchId) + ' Failed')
            else:
                time.sleep(120)
    
    if match['human_players'] != 10 or len(match['players']) != 10:
        raise APIError('Bad number of players')
    if 'radiant_win' not in match.viewkeys():
        raise APIError('Match not completed')
    matchRow = [0]*15
    matchRow[0] = matchId
    if match['radiant_win']: # eg True
        matchRow[1] = 1
    else:
        matchRow[1] = -1
    matchRow[2] = match['cluster'] # eg 227 -> translates to Europe West?
    matchRow[3] = match['game_mode_name'] # eg Captains Mode
    matchRow[4] = match['lobby_name'] # eg Ranked
    for i in range(10):
        matchRow[5 + i] = match['players'][i]['hero_id'] # eg 5

    return matchRow

def serialLoop( api, matchId, stopNum, writer ):
    while stopNum > 0:
        try:
            matchInfo = getMatchInfo( api, matchId )
            writer.writerow(matchInfo)
            stopNum -= 1
            print "Got " + str(matchId) + ", Need " + str(stopNum) + " more"
        except APIError as e:
            print e.msg
        finally:
            matchId -= 1

def getMatchStar( args ):
    try:
        match = getMatchInfo( args[0], args[1] )
        print "Match " + str(args[1]) + " successful"
        return match
    except APIError as e:
        print e.msg
    return []
        
def parallelLoop( api, matchId, stopNum, writer ):
    p = Pool(4)

    matchList = ( [ (api, matchId - x ) for x in range(2*stopNum) ] )
    for x in p.map(getMatchStar, matchList):
        if len(x) != 0:
            writer.writerow( x )
    p.terminate()

if __name__=="__main__":
    api = dota2api.Initialise()
    matchId = 2561608200
    ### matchSeqNum = 2242825642
    stopNum = 100000
    outFile = open('dotaMatch.out', 'a')
    writer = csv.writer(outFile)

    serialLoop( api, matchId, stopNum, writer )
    #parallelLoop( api, matchId, stopNum, writer )
    
    outFile.close()