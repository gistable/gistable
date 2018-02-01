#!/usr/bin/env python2
import json
import random
import copy
import googlemaps
import math
import os.path
import datetime

def distanceFromLarAndLon(lon1, lat1, lon2, lat2):
    """
    Compute the distance between 2 GPS points

    :param lon1: longitude of the first point
    :param lat1: latitude of the first point
    :param lon2: longitude of the first point
    :param lat2: latitude of the first point
    :return:
    """
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    R = 6371000
    x = (lon2 - lon1) * math.cos(0.5 * (lat2 + lat1))
    y = lat2 - lat1
    return R * math.sqrt(x * x + y * y)

class loopFinder:
    """
    Search for most efficient path among spanws identified by TBTera script
    """
    def __init__(self):



        self.pointsOfInterest = []

        self.currentGPSPosition = {'lat':48.814687, 'lng':2.234803, 'pointType':'CurrentGPSPosition'}
        self.pointsOfInterest.append(self.currentGPSPosition)


        with open('spawns.json') as file:
            self.spawns = json.load(file)
        for spawn in self.spawns:
            spawn['pointType'] = 'spawn'
            self.pointsOfInterest.append(spawn)


        with open('stops.json') as file:
            self.stops= json.load(file)
        for stop in self.stops:
            stop['pointType'] = 'stop'
            self.pointsOfInterest.append(stop)


        self.availableTime = 900 #seconds
        self.distances = self.computeDistanceMatrix()
        self.N = int(math.sqrt(len(self.distances)))
        self.walkSpeed = 4

        myPath = dict()

        self.startWalkingNow = True
        self.closedPath = False
        now=datetime.datetime.now()
        myPath['startTime'] = now.minute*60 +now.second
        myPath['steps'] = [0]

        self.bestPath = self.SimulatedAnnealing(myPath, self.availableTime, 15000)
        self.computePathXPAndDuration(self.bestPath, True)
        self.dumpBestPathJson()

    def loadDistanceMatrix(self):
        if os.path.isfile('distances_.json'):
            with open('distances.json') as file:
                   distances = json.load(file)
        else:
            distances = self.computeDistanceMatrix()
        return distances

    def askGoogleDistanceMatrix(self, npSpawnsConsidered):
        with open('spawns.json') as file:
            spawns = json.load(file)
        points=[]

        for spawn in spawns:
            points.append((spawn['lat'], spawn['lng']))
        points = points[:npSpawnsConsidered]

        gmaps = googlemaps.Client(key='XXXXXXXXXXXXXXXX')

        distanceMatrix = gmaps.distance_matrix(points, points)

        distances = []
        for row in distanceMatrix['rows']:
            for element in row['elements']:
                distances.append(element['distance']['value'])

        f = open('distances.json','w')
        json.dump(distances,f)
        f.close()

        return distances

    def computeDistanceMatrix(self):
        # #spawn file

        pointsOfInterest = copy.deepcopy(self.pointsOfInterest)
        points=[]

        for pointOfInterest in pointsOfInterest:
            points.append((pointOfInterest['lat'], pointOfInterest['lng']))
        N = len(pointsOfInterest)

        distances = []
        for i in range(N):
            for j in range(N):
                distanceIJ = distanceFromLarAndLon(points[i][1], points[i][0], points[j][1], points[j][0])
                distances.append(distanceIJ )
        #and yes, it is a symetrical matrix...





        return distances

    def distanceIJ(self, i,j):
        distances = self.distances
        N = int(math.sqrt(len(distances)))
        return distances[i*N+j]

    def computePathXPAndDuration(self, path, document=False):
        distances = self.distances
        pointsOfInterest = copy.deepcopy(self.pointsOfInterest)
        for pointOfInterest in pointsOfInterest:
            pointOfInterest['nextAvailableTime'] = -1

        currentXP = 0

        currentPoint = path['steps'][0]

        currentTime = path['startTime'] #in seconds

        loopedPathOrNot =path['steps'][1:]
        if not(self.closedPath):
            loopedPathOrNot.append(currentPoint) #I want to compute loops : I go back to my starting point

        for step in loopedPathOrNot:
            currentTime = currentTime + int(float(self.distanceIJ(currentPoint, step)) / (self.walkSpeed * 1000) * 60*60)
            availableTime = pointsOfInterest[step]['nextAvailableTime']

            if pointsOfInterest[step]['pointType'] == 'spawn':
                spawnTime = pointsOfInterest[step]['time']
                spanwSinceXsec =(currentTime%3600 - spawnTime) % 3600
                if spanwSinceXsec < 900 and availableTime<currentTime:
                    if document:
                        print("We are in step {} and the currentTime is {}, you got a pokemon who had spawnTime {}, which spawn {} ago".format(step, currentTime, spawnTime, spanwSinceXsec))
                    #the spawn is active
                    currentXP = currentXP+100
                    pointsOfInterest[step]['nextAvailableTime'] = currentTime - spanwSinceXsec + 3600


            if pointsOfInterest[step]['pointType'] == 'stop':
                if availableTime < currentTime:
                    currentXP = currentXP + 50
                    pointsOfInterest[step]['nextAvailableTime'] = currentTime + 300
                if document:
                    print("We are in step {} and the currentTime is {}, you got a pokestop".format(step, currentTime))

            currentPoint = step

        return currentXP, currentTime-path['startTime']

    def getClosePath(self, path_):
        path=copy.deepcopy(path_) #If you do not do that you have path_ mutable !

        for i in range(random.randint(1,2)): #I allow 1 to 2 modifications of the path


            if self.startWalkingNow:
                pathModification = random.randint(2,5)
            else:
                pathModification = random.randint(1,5)
            # 1 -> we change the startTime
            # 2 -> we add a point
            # 3 -> we delete a point
            # 4 -> we replace a point by another
            # 5 -> we swap two steps of our path

            if pathModification==1: #change startTime
                path['startTime'] = random.randint(0,3599)

            if pathModification==2: #insert a step
                index = random.randint(1,max(len(path['steps'])-1,1)) #I keep step (startPoint as is)
                allPlausibleInsertedSteps = range(self.N)

                if index<len(path['steps']):
                    toRemoveFromPossibleNewCommers = path['steps'][index]
                    if toRemoveFromPossibleNewCommers in allPlausibleInsertedSteps:
                        allPlausibleInsertedSteps.remove(toRemoveFromPossibleNewCommers)

                if index-1>0:
                    toRemoveFromPossibleNewCommers = path['steps'][index-1]
                    if toRemoveFromPossibleNewCommers in allPlausibleInsertedSteps:
                        allPlausibleInsertedSteps.remove(toRemoveFromPossibleNewCommers)

                stepInserted = random.sample(allPlausibleInsertedSteps,1)[0]
                path['steps'].insert(index, stepInserted)

            if pathModification==3: #delete a step
                if len(path['steps'])>1:
                    index = random.randint(1,len(path['steps'])-1) #I keep step 0(startPoint as is)
                    path['steps'].pop(index)
                    if index<len(path['steps']):
                        #we ensure there will not be two consecutive steps equal
                        if path['steps'][index] ==  path['steps'][index-1]:
                            path['steps'].pop(index)

            if pathModification == 4:  # replace a step by another step
                index = random.randint(1,max(len(path['steps']) - 1, 1))  # I keep step (startPoint as is)
                allPlausibleInsertedSteps = range(self.N)


                if index<len(path['steps'])-1:
                    toRemoveFromPossibleNewCommers = path['steps'][index+1]
                    if toRemoveFromPossibleNewCommers in allPlausibleInsertedSteps:
                        allPlausibleInsertedSteps.remove(toRemoveFromPossibleNewCommers)

                if index-1>0:
                    toRemoveFromPossibleNewCommers = path['steps'][index-1]
                    if toRemoveFromPossibleNewCommers in allPlausibleInsertedSteps:
                        allPlausibleInsertedSteps.remove(toRemoveFromPossibleNewCommers)

                if index <len(path['steps']):
                    path['steps'][index] = random.sample(allPlausibleInsertedSteps, 1)[0]

        if pathModification == 5:  # swap two steps
            if len([path['steps']])>2:
                sampledSteps = random.sample(range(1,len(path['steps']))-1)
                temp = path['steps'][sampledSteps[0]]
                path['steps'][sampledSteps[0]] = path['steps'][sampledSteps[1]]
                path['steps'][sampledSteps[1]] = temp

        return path

    def GetPathEnergy(self, path, timeLimit):
        distances = self.distances
        PathXP, PathDuration = self.computePathXPAndDuration(path)
        return -(float(PathXP) - math.exp(min((PathDuration-timeLimit)/60, 20)) )

    def SimulatedAnnealing(self, path, timeLimit, iterations):
        distances = self.distances
        T=360000000
        freeze = 0.99

        currentPath = dict(path)
        currentEnergy= self.GetPathEnergy(currentPath, timeLimit)

        for i in range(iterations):
            candidatePath = self.getClosePath(currentPath)
            candidatePathEnergy= self.GetPathEnergy(candidatePath, timeLimit)

            if candidatePathEnergy<currentEnergy:
                currentPath = dict(candidatePath)
                currentEnergy = candidatePathEnergy
            else:
                if random.uniform(0,1)<math.exp(-(candidatePathEnergy-currentEnergy)/T):
                    currentPath = dict(candidatePath)
                    currentEnergy = candidatePathEnergy
            T = freeze * T


            #print ('Iteration : {} \t T : {} \t currentEnergy : {}').format(i, T, currentEnergy)

        print currentPath
        PathXP, PathDuration = self.computePathXPAndDuration(currentPath)
        currentEnergy = self.GetPathEnergy(currentPath, timeLimit)
        print ('PathXP : {}, PathDuration : {}, FinalEnergy {} ').format(PathXP, PathDuration, currentEnergy)

        if self.closedPath:
            currentPath['steps'].append(0)

        return currentPath

    def dumpBestPathJson(self):
        out = []
        pointsOfInterest = self.pointsOfInterest
        for step in self.bestPath['steps']:
            pointToInsert = dict()
            pointToInsert['lat'] = pointsOfInterest[step]['lat']
            pointToInsert['lng'] = pointsOfInterest[step]['lng']
            out.append(pointToInsert)

        f = open('bestPath.json', 'w')
        json.dump(out, f)
        f.close()



myLoopFinder = loopFinder()