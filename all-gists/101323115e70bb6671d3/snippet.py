'''
Created on Feb 8, 2015

@author: David Ray
'''

import numpy as np

from nupic.encoders.scalar import ScalarEncoder as ScalarEncoder
from nupic.algorithms.CLAClassifier import CLAClassifier as CLAClassifier
from nupic.research.spatial_pooler import SpatialPooler as SpatialPooler
from nupic.research.temporal_memory import TemporalMemory as TemporalMemory
from nupic.algorithms import anomaly


class Layer():
    
    """ Makeshift Layer to contain and operate on algorithmic entities """
    
    def __init__(self, encoder, sp, tm, classifier):
        
        self.encoder = encoder
        self.sp = sp
        self.tm = tm
        self.classifier = classifier
        self.theNum = 0
        self.weeksAnomaly = 0.0
        self.settleWeek = 0
        
        
    def input(self, value, recordNum, sequenceNum):
        """ Feed the incremented input into the Layer components """
         
        if recordNum == 1:
            recordOut = "Monday (1)"
        elif recordNum == 2:
            recordOut = "Tuesday (2)"
        elif recordNum == 3:
            recordOut = "Wednesday (3)"
        elif recordNum == 4:
            recordOut = "Thursday (4)"
        elif recordNum == 5:
            recordOut = "Friday (5)"
        elif recordNum == 6:
            recordOut = "Saturday (6)"
        else: recordOut = "Sunday (7)"
        
        if recordNum == 1:
            self.theNum += 1
             
            print "--------------------------------------------------------"
            print "Iteration: " + str(self.theNum)
            
            self.weeksAnomaly = 0
            
        print "===== " + str(recordOut) + " - Sequence Num: " + str(sequenceNum) + " ====="
        
        output = np.zeros(sp._columnDimensions)
        
        # Input through encoder
        print "ScalarEncoder Input = " + str(value)
        encoding = encoder.encode(value)
        print "ScalarEncoder Output = " + str(encoding)
        bucketIdx = encoder.getBucketIndices(value)[0]
        
        # Input through spatial pooler
        sp.compute(encoding, True, output)
        print "SpatialPooler Output = " + str(output)
        
        # Input through temporal memory
        activesCols = sorted(set(np.where(output > 0)[0].flat))
        tm.compute(activesCols, True)        
        activeCells = tm.getActiveCells() #getSDR(tm.predictiveCells)
        predictiveCells = tm.getPredictiveCells()
        print "TemporalMemory Input = " + str(input)
        
        # Input into Anomaly Computer
        predictiveCols = set()
        for c in predictiveCells:
            predictiveCols.add(tm.columnForCell(c))
        predictiveCols = sorted(predictiveCols)
        score = anomaly.computeRawAnomalyScore(activesCols, predictiveCols)
        print "input: " + str(activesCols)
        print "predi: " + str(predictiveCols) 
        print "Anomaly Score: " + str(score)
        self.weeksAnomaly += score
        
        if recordNum == 7 and self.weeksAnomaly == 0 and self.settleWeek == 0:
            self.settleWeek = self.theNum
        
        
        # Input into classifier
        retVal = classifier.compute(recordNum,
            patternNZ=activeCells,
            classification= {'bucketIdx': bucketIdx, 'actValue':value},
            learn=True,
            infer=True
        )
        
        print "TemporalMemory Prediction = " + str(getSDR(activeCells)) +\
        "  |  CLAClassifier 1 step prob = " + str(retVal[1]) 
        print ""
        
    def getWeeksAnomaly(self):
        return self.weeksAnomaly
    
    def getWeek(self):
        return self.theNum
    
    def getSettleWeek(self):
        return self.settleWeek

def getSDR(cells):
    retVal = set()
    for cell in cells:
        retVal.add(cell / tm.cellsPerColumn)
    return retVal     
        
def runThroughLayer(layer, recordNum, sequenceNum):
    
    layer.input(recordNum, recordNum, sequenceNum)        
        
        
if __name__ == '__main__':
    encoder = ScalarEncoder(
        n = 8,
        w = 3,
        radius = 0,
        minval = 1,
        maxval = 8,
        periodic = True,
        forced = True,
        resolution = 0
    )
    
    sp = SpatialPooler(
        inputDimensions = (8),
        columnDimensions = (20),
        potentialRadius = 12,
        potentialPct = 0.5,
        globalInhibition = True,
        localAreaDensity = -1.0,
        numActiveColumnsPerInhArea = 5.0,
        stimulusThreshold = 1.0,
        synPermInactiveDec = 0.0005,
        synPermActiveInc = 0.0015,
        synPermConnected = 0.1,
        minPctOverlapDutyCycle = 0.1,
        minPctActiveDutyCycle = 0.1,
        dutyCyclePeriod = 10, 
        maxBoost = 10.0,
        seed = 42,
        spVerbosity = 0
    )
    
    tm = TemporalMemory(
        columnDimensions = (20,),
        cellsPerColumn = (6),
        initialPermanence = 0.2,
        connectedPermanence = 0.8,
        minThreshold = 5,
        maxNewSynapseCount = 6,
        permanenceDecrement = 0.1,
        permanenceIncrement = 0.1,
        activationThreshold = 4
    )
    
    classifier = CLAClassifier(
        steps = [1],
        alpha = 0.1,
        actValueAlpha = 0.3,
        verbosity = 0
    )
    
    sp.printParameters()
    print ""
    
    layer = Layer(encoder, sp, tm, classifier)
    
    firstWeek = 0
    
    i = 1
    for x in range(2000):
        if i == 1:
            tm.reset()
            if firstWeek == 0 and layer.getWeeksAnomaly() > 0 and layer.getWeeksAnomaly() < 7.0:
                firstWeek = layer.getWeek()
            
        runThroughLayer(layer, i, x)
        i = 1 if i == 7 else i + 1
        
    print "firstWeek = " + str(firstWeek)
    print "settleWeek = " + str(layer.getSettleWeek())    
    