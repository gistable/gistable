## Generate a full season's worth of batting Marcel projections from past years' stats

from createTuple import createTuple ## gist: 778481
from writeMatrixCSV import writeMatrixCSV ## gist: 778484

def makeBatTable(r):
    for stat in ['AB', 'H', 'D', 'T', 'HR', 'SO', 'BB', 'SF', 'HP', 'CI']:
        if stat in r:   pass
        else:   r[stat] = 0
    if r['AB'] == 0:
        r['SLG'] = 0
        r['AVG'] = 0
        slg = 0
    else:
        avg = float(r['H'])/float(r['AB'])
        r['AVG'] = round(avg, 3)
        slg = float(r['H']+r['D']+(2*r['T'])+(3*r['HR']))/float(r['AB'])
        r['SLG'] = round(slg, 3)
    if (r['AB']+r['BB']+r['SF']+r['HP']) == 0:
        r['OBP'] = 0
        r['OPS'] = 0
        r['wOBA'] = 0
    else:
        pa = float(r['AB']+r['BB']+r['SF']+r['HP']+r['CI'])
        obp = float(r['H']+r['BB']+r['HP']+r['CI'])/pa
        r['OBP'] = round(obp, 3)
        sing = int(r['H']) - int(r['HR']) - int(r['T']) - int(r['D'])
        num = (.72*int(r['BB'])) + (.75*int(r['HP'])) + (.9*sing) + (1.24*int(r['D'])) + (1.56*int(r['T'])) + (1.95*int(r['HR']))
        den = int(r['BB']) + int(r['AB']) + int(r['HP'])
        woba = num/den
        r['wOBA'] = round(woba, 3)
    return r
    
def marcelBattingSeason(yr):
    # yr = year being projected, input as int
    yr = str(yr) 
    yr1 = str(int(yr) - 1)
    yr2 = str(int(yr) - 2)
    yr3 = str(int(yr) - 3)

    ## get list of pitchers; determine which batters are really
    ## 'batters' and throw out pitchers with at-bats
    projectBatters = []
    for yr in [yr3, yr2, yr]:
        yearPitchers = {}
        for p in pitchers:
            pitchID = p[0]
            if p[1] == yr:
                yearPitchers[pitchID] = int(p[12])
            else:   pass
        for b in batters:
            batID = b[0]
            if b[1] == yr:  pass
            else:   continue
            abString = b[7]
            if abString == '':  continue
            else:   batAb = int(abString)
            if batID in yearPitchers:
                if yearPitchers[batID] > batAb: continue
                else:   pass
            else:   pass
            if batID in projectBatters: pass
            else:   projectBatters.append(batID)

    ## find league average for previous year
    yearPitchers = {}
    for p in pitchers:
        pitchID = p[0]
        if p[1] == yr1:
            yearPitchers[pitchID] = int(p[12])
        else:   pass

    leagueAverage = {}
    for b in batters:
        batID = b[0]
        if b[1] == yr1:  pass
        else:   continue
        abString = b[7]
        if abString == '':  continue
        else:   batAb = int(abString)
        if batID in yearPitchers:
            if yearPitchers[batID] > batAb: continue
            else:   pass
        else:   pass
        if batID in projectBatters: pass
        else:   projectBatters.append(batID)
        for stat in batHeaders:
            col = batHeaders[stat]
            try:    playerStat = int(b[col])
            except: continue
            else:   pass
            if stat in leagueAverage:
                leagueAverage[stat] += playerStat
            else:
                leagueAverage[stat] = playerStat

    for stat in ['HP', 'SF', 'SH']:
        if stat in leagueAverage:   pass
        else:   leagueAverage[stat] = 0
    totalPa = leagueAverage['AB'] + leagueAverage['BB'] + leagueAverage['HP'] + leagueAverage['SF'] + leagueAverage['SH']
    regression = {}
    for stat in leagueAverage:
        regression[stat] =(1200.0/totalPa)*leagueAverage[stat]

    rawProjections = {}

    ## calculate projections for each player
    for b in projectBatters:
        components = {}
        y2pa = 0
        y1pa = 0
        for stat in batHeaders:
            components[stat] = 0
        for row in batters:
            if row[0] == b: pass
            else:   continue
            if row[1] == yr3:
                for stat in batHeaders:
                    try:    playerStat = int(row[batHeaders[stat]])
                    except: continue
                    components[stat] += 3*playerStat
            elif row[1] == yr2:
                for stat in batHeaders:
                    try:    playerStat = int(row[batHeaders[stat]])
                    except: continue
                    components[stat] += 4*playerStat
                
                for stat in ['AB', 'BB', 'HP', 'SF', 'SH']:
                    try:    y2pa += int(row[batHeaders[stat]])
                    except: continue                
            elif row[1] == yr1:
                for stat in batHeaders:
                    try:    playerStat = int(row[batHeaders[stat]])
                    except: continue
                    components[stat] += 5*playerStat
                
                for stat in ['AB', 'BB', 'HP', 'SF', 'SH']:
                    try:    y1pa += int(row[batHeaders[stat]])
                    except: continue
            else:   continue
        ## add regression component
        for stat in regression:
            components[stat] += regression[stat]
        ## get projected PA
        projPa = 0.5*y1pa + 0.1*y2pa + 200
        ## prorate into projected PA
        compPa = components['AB'] + components['BB'] + components['HP'] + components['SF'] + components['SH']
        prorateProj = {}
        for stat in components:
            prorateProj[stat] = (projPa/compPa)*components[stat]
        prorateProj['PA'] = projPa
        try:    age = int(yr) - int(birthYear[b])
        except: age = 29 ## in case birthyear is missing or corrupted
        ## age adjust
        if age > 29:
            ageAdj = 1/(1 + ((age - 29)*0.003))
        elif age < 29:
            ageAdj = 1 + ((29 - age)*0.006)
        else:
            ageAdj = 1
        finalProj = {}
        for stat in prorateProj:
            if stat in ['PA', 'AB']:
                finalProj[stat] = prorateProj[stat]
            elif stat in ['R', 'H', 'D', 'T', 'HR', 'RBI', 'SB', 'BB', 'IBB', 'HP', 'SH', 'SF']:
                finalProj[stat] = prorateProj[stat]*ageAdj
            else:
                finalProj[stat] = prorateProj[stat]/ageAdj
        ## reliability
        reliab = 1 - (1200.0/compPa)
        finalProj['rel'] = round(reliab, 2)
        finalProj['Age'] = age
        ## add to master dict
        rawProjections[b] = finalProj

    ## re-baseline
    projTotal = {}
    for pl in rawProjections:
        for stat in rawProjections[pl]:
            if stat in projTotal:
                projTotal[stat] += rawProjections[pl][stat]
            else:
                projTotal[stat] = rawProjections[pl][stat]
    projTotalPa = projTotal['PA']
    projRatios = {}
    for stat in ['AB', 'R', 'H', 'D', 'T', 'HR', 'RBI', 'SB', 'CS', 'BB', 'SO', 'IBB', 'HP', 'SH', 'SF', 'GDP']:
        projRatios[stat] = projTotal[stat]/projTotalPa

    trueRatios = {}
    for stat in ['AB', 'R', 'H', 'D', 'T', 'HR', 'RBI', 'SB', 'CS', 'BB', 'SO', 'IBB', 'HP', 'SH', 'SF', 'GDP']:
        try:    trueRatios[stat] = leagueAverage[stat]/float(totalPa)
        except: trueRatios[stat] = 0

    marcels = {}
    for pl in rawProjections:
        marcels[pl] = {}
        for stat in rawProjections[pl]:
            if stat in ['AB', 'R', 'H', 'D', 'T', 'HR', 'RBI', 'SB', 'CS', 'BB', 'SO', 'IBB', 'HP', 'SH', 'SF', 'GDP']:
                if projRatios[stat] == 0:
                    marcels[pl][stat] = rawProjections[pl][stat]
                else:
                    marcels[pl][stat] = round((trueRatios[stat]/projRatios[stat])*rawProjections[pl][stat], 0)
            elif stat == 'PA':
                marcels[pl][stat] = round(rawProjections[pl][stat], 0)
            else:
                marcels[pl][stat] = rawProjections[pl][stat]

    header = ['bdbID', 'First', 'Last', 'Year', 'age', 'rel', 'wOBA', 'AVG', 'OBP', 'SLG',
                     'PA', 'AB', 'R', 'H', 'D', 'T', 'HR', 'RBI',
                     'SB', 'CS', 'BB', 'SO', 'IBB', 'HP', 'SH', 'SF', 'GDP']

    marcelSheet = [header]
    for pl in marcels:
        row = [pl]
        row += firstlast[pl]
        row.append(yr)
        marcels[pl] = makeBatTable(marcels[pl])
        for stat in ['Age', 'rel', 'wOBA', 'AVG', 'OBP', 'SLG',
                     'PA', 'AB', 'R', 'H', 'D', 'T', 'HR', 'RBI',
                     'SB', 'CS', 'BB', 'SO', 'IBB', 'HP', 'SH', 'SF', 'GDP']:
            row.append(marcels[pl][stat])
        marcelSheet.append(row)

    filename = 'marcel_batters_' + yr + '.csv'
    writeMatrixCSV(marcelSheet, filename)

batHeaders = {'AB': 7,
              'R': 8,
              'H': 9,
              'D': 10,
              'T': 11,
              'HR': 12,
              'RBI': 13,
              'SB': 14,
              'CS': 15,
              'BB': 16,
              'SO': 17,
              'IBB': 18,
              'HP': 19,
              'SH': 20,
              'SF': 21,
              'GDP': 22
              }


pitchers = createTuple('bdb_pitching.csv')
## this is the pitcher seasons sheet from the lahman db.  headers:
## playerID,yearID,stint,teamID,lgID,W,L,G,GS,CG,SHO,SV,Ipouts,H,ER,HR,BB,SO,Baopp,ERA,IBB,WP,HP,BK,BFP,GF,R

batters = createTuple('bdb_batting.csv')
## this is the batting seasons sheet from the lahman db.  headers:
## playerID,yearID,stint,teamID,lgID,G,G_batting,AB,R,H,D,T,HR,RBI,SB,CS,BB,SO,IBB,HP,SH,SF,GIDP,G_old

## master db for birthYear
master = createTuple('bdb_master.csv')
## master biographical data sheet from lahman db.  headers:
## lahmanID,playerID,managerID,hofID,birthYear,birthMonth,birthDay,birthCountry,birthState,birthCity,deathYear,deathMonth,deathDay,deathCountry,deathState,deathCity,nameFirst,nameLast,nameNote,nameGiven,nameNick,weight,height,bats,throws,debut,finalGame,college,lahman40ID,lahman

birthYear = {}
for pl in master:
    birthYear[pl[1]] = pl[4]

firstlast = {}
for pl in master:
    firstlast[pl[1]] = [pl[16], pl[17]]

## sample usage 
marcelBattingSeason(2005)