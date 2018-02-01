#Author: Marcel Pinheiro Caraciolo
#Confusion Matrix Generator
#Version: 0.1
#email: caraciol at gmail . com


from pprint import pprint as _pretty_print
import math

class ConfusionMatrix(object):
	''' Confusion Matrix for single-labeled categorization.
	 	i.e each instance belongs only to one class.
	'''
	
	def __init__(self, classes):
		''' Init a empty confusion matrix.
		
			Params:
				classes: An interable over the classes (labels).
				
		'''
		self._labels = tuple(classes)
		self._matrix = [ [0.0 for j in range(len(self._labels))] for i in range(len(self._labels))  ]
		
	
	def getLabels(self):
		
		''' Return the label categories. '''
		return self._labels
	
	def getConfusionMatrix(self):
		''' Returns the confusion Matrix '''
		return self._matrix
	
	def setData(self,originals,arrays):
		''' Set the confusion matrix from the countable arrays.
			Params:
				originals: An interable over the (input,Actlabel)
				arrays: An interable over the (input,predLabel)
		'''

		#actual
		r_temp = {}
		for input,labelO in originals:
			try:
				index = list(self._labels).index(labelO)
			except ValueError:
				raise Exception('label %s not found. check the labels.' % label0)
				
			#predicted
			for input2,labelR in arrays:
				
				if input == input2:
					try:
						index2 = list(self._labels).index(labelR)
					except ValueError:
						raise Exception('label %s not found. check the labels.' % labelR)
						
					self._matrix[index2][index]+=1
					arrays.remove((input2,labelR))
					break
			else:
				print '**WARNING** :Not found the output for input ' + str(input)
		
	def drawConfusionMatrix(self):
		''' Draw the Confusion Matrix '''
		table = []
		#header
		table.append([''] + list(self._labels))
		#class metrics
		for c in range(len(self._matrix)):
			table.append([self._labels[c]] + self._matrix[c])
		#averaging metrics
		for prefix in ['TNR/TPR']:
			table.append([prefix] + [self.sensitivity(), self.specificity()])
			
		return  _pretty_print(table)
			
		
	def accuracy(self):
		''' Evaluate the accuracy. '''
		result = {}
		total = 0.0
		for i in range(len(self._labels)):
			try:
				result[self._labels[i]] = self._matrix[i][i] / sum(self._matrix[i])
				total += result[self._labels[i]]
			except ZeroDivisionError:
				result[self._labels[i]] = None
				total += 0.0
		
		result['overall'] = total / float(len(self._labels))
		return result
	
	def sensitivity(self):
		'''Evaluate the sensitivity (Only work in 2x2 confusion matrixes)'''
		if len(self._labels) == 2:
			return float(self._matrix[0][0]) / (self._matrix[0][0] + self._matrix[1][0] or 1.0)
			
		else:
			raise Exception('Problems with the evaluation: It must be 2x2 confusion matrix')

	def specificity(self):
		'''Evaluate the specificity (Only work in 2x2 confusion matrixes)'''
		if len(self._labels) == 2:
			return float(self._matrix[1][1]) / ((self._matrix[1][1] + self._matrix[0][1]) or 1.0)
		else:
			raise Exception('Problems with the evaluation: It must be 2x2 confusion matrix')
		
	def efficiency(self):
		''' Evaluate the efficiency  (Only work in 2x2 confusion matrixes) '''
		if len(self._labels) == 2:
			return (self.specificity() + self.sensitivity()) / 2.0
		else:
			raise Exception('Problems with the evaluation: It must be 2x2 confusion matrix')
			
	def positivePredictiveValue(self):
		''' Evalute the PPV which indicates how likely is that a given input has the target condition, given that
		    the input is really positive. (Only work in 2x2 confusion matrixes) 
		'''
		if len(self._labels) == 2:
			return float(self._matrix[0][0]) / ((self._matrix[0][0] + self._matrix[0][1]) or 1.0 )
		else:
			raise Exception('Problems with the evaluation: It must be 2x2 confusion matrix')
		
		
	def negativePredictiveValue(self):
		''' Evalute the NPV which indicates how likely is that a given input does not has the target condition, given that
		    the input is really negative. (Only work in 2x2 confusion matrixes) 
		'''
		if len(self._labels) == 2:
			return float(self._matrix[1][1]) / ((self._matrix[1][1] + self._matrix[1][0]) or 1.0 )
		else:
			raise Exception('Problems with the evaluation: It must be 2x2 confusion matrix')
			
	def phiCoefficient(self):
		''' A coefficient of +1 represents a perfect prediction , 0 an averagem random prediction
			and -1 an inverse prediction.
		'''
		result = math.sqrt(
		                 (self._matrix[0][0] + self._matrix[0][1]) *
						 (self._matrix[0][0] + self._matrix[1][0]) *
						 (self._matrix[1][1] + self._matrix[0][1]) *
						 (self._matrix[1][1] + self._matrix[1][0]))
		if result:
			return (self._matrix[0][0] * self._matrix[1][1]) / float(result)
		else:
			return 0.0
		
		
if __name__ == '__main__':
	x = ConfusionMatrix((['Positive','Negative']))
	dataSet = [(i,'Positive') for i in range(3)] + [(i,'Negative') for i in range(3,203)]
	output = [(i,'Positive') for i in range(2)] + [(i,'Negative') for i in range(2,3)] + \
                 [(i,'Positive') for i in range(3,21)] + [(i,'Negative') for i in range(21,203)]
	x.setData(dataSet,output)
	print 'Accuracy', x.accuracy()
	print 'Sensitivity',x.sensitivity()
	print 'Specificity', x.specificity()
	print 'Efficiency' , x.efficiency()
	print 'Positive Predictive Value', x.positivePredictiveValue()
	print 'Negative Predictive Value', x.negativePredictiveValue()
	print 'Phi Coefficient' , x.phiCoefficient()
	x.drawConfusionMatrix()
