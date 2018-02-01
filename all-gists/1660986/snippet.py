import sys

def negVector(lst):
  return [-x for x in lst]

def addVectors(l1, l2):
  return [l1[i] + l2[i] for i in range(len(l1))]

def multVectors(l1, l2):
  return [l1[i] * l2[i] for i in range(len(l1))]

def dot(l1, l2):
  return sum(multVectors(l1, l2))

class DataPoint:
  def __init__(self, i, a, f):
    self.identifier = i
    self.answer = a
    self.features = f

# Basic binary perceptron classifier
class Classifier:
  weights = []
  iterations = 10

  def __init__(self, numWeights):
    self.weights = [0 for i in range(numWeights)]
  
  def train(self, trainingData):
    for i in range(self.iterations):
      for datum in trainingData:
        y = (dot(self.weights, datum.features) > 0)
        yStar = datum.answer
        if y != yStar:
          adjustment = datum.features if yStar else negVector(datum.features)
          # tau = (dot(self.weights, datum.features) + 1) / dot(datum.features, datum.features)
          # adjustment = [tau * x for x in adjustment] # MIRA adjustment
          self.weights = addVectors(self.weights, adjustment)
          # print self.weights
        
  def classify(self, data):
    for datum in data:
      y = (dot(self.weights, datum.features) > 0)
      print datum.identifier, '+1' if y else '-1' #, dot(self.weights, datum.features)

trainingData = []
data = []

firstLine = map(int, sys.stdin.readline().split())
trainingRecordsLeft = firstLine[0]
numParams = firstLine[1]
while (trainingRecordsLeft > 0):
  line = sys.stdin.readline().split()
  identifier = line[0]
  answer = (line[1] == '+1')
  features = [0 for i in range(numParams)]
  for i in range(2, len(line)):
    featureChunk = line[i].split(':')
    featureNum = int(featureChunk[0]) - 1
    featureValue = float(featureChunk[1])
    features[featureNum] = featureValue
  datum = DataPoint(identifier, answer, features)
  trainingData.append(datum)
  trainingRecordsLeft -= 1
recordsLeft = int(sys.stdin.readline())

# The features have values that are orders of magnitudes in difference - we normalize them by 
# setting the greatest to be +/- 1. The normalizer is the vector we multiply the features against
def maxFeatureValue(paramNum):
  return abs(max([trainingData[j].features[paramNum] for j in range(len(trainingData))]))
normalizer = [(1 / maxFeatureValue(i) if maxFeatureValue(i) > 0 else 0) for i in range(numParams)]
# print normalizer

for datum in trainingData:
  datum.features = multVectors(datum.features, normalizer)

while (recordsLeft > 0):
  line = sys.stdin.readline().split()
  identifier = line[0]
  features = [0 for i in range(numParams)]
  for i in range(1, len(line)):
    featureChunk = line[i].split(':')
    featureNum = int(featureChunk[0]) - 1
    featureValue = float(featureChunk[1])
    features[featureNum] = featureValue
  features = multVectors(features, normalizer)
  datum = DataPoint(identifier, '', features)
  data.append(datum)
  recordsLeft -= 1

classifier = Classifier(numParams)
classifier.train(trainingData)
# print classifier.weights
classifier.classify(data)

# History
# v1.1 Oops, debug output
# v1.0 Initial submission
