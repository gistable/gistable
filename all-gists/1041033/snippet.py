import sys, os, glob
from datetime import datetime

sys.path.append(os.environ.get("MAHOUT_CORE"))
for jar in glob.glob(os.environ.get("MAHOUT_JAR_DIR") + "/*.jar"):
	sys.path.append(jar)
	
from org.apache.mahout.common import RandomUtils
from org.apache.mahout.cf.taste.common import TasteException
from org.apache.mahout.cf.taste.eval import *
from org.apache.mahout.cf.taste.impl.eval import *
from org.apache.mahout.cf.taste.impl.model.file import *
from org.apache.mahout.cf.taste.impl.neighborhood import *
from org.apache.mahout.cf.taste.impl.recommender import GenericUserBasedRecommender
from org.apache.mahout.cf.taste.impl.recommender.slopeone import SlopeOneRecommender
from org.apache.mahout.cf.taste.impl.similarity import *
from org.apache.mahout.cf.taste.model import *
from org.apache.mahout.cf.taste.neighborhood import *
from org.apache.mahout.cf.taste.recommender import *
from org.apache.mahout.cf.taste.similarity import *
from java.io import *
from java.util import *

class GenericRecommenderBuilder(RecommenderBuilder):
	def __init__(self):
		pass
	def buildRecommender(self, model):
		similarity = PearsonCorrelationSimilarity(model)
		neighborhood = NearestNUserNeighborhood(2, similarity, model)
		return GenericUserBasedRecommender(model, neighborhood, similarity)

class SlopeOneRecommenderBuilder(RecommenderBuilder):
	def __init__(self):
		pass
	def buildRecommender(self, model):
		similarity = PearsonCorrelationSimilarity(model)
		neighborhood = NearestNUserNeighborhood(2, similarity, model)
		return SlopeOneRecommender(model)

def main():
	RandomUtils.useTestSeed()
	model = FileDataModel(File(sys.argv[1]))
	builder = GenericRecommenderBuilder()

	print 'Starting run at %s' % datetime.now()
	for builder in [GenericRecommenderBuilder(), SlopeOneRecommenderBuilder()]:
		print 'Starting evaluations of recommender created using %s at %s...' % (builder, datetime.now())
		for evaluator in [AverageAbsoluteDifferenceRecommenderEvaluator(), RMSRecommenderEvaluator()]:
			print 'Evaluating recommender using %s at %s...' % (evaluator, datetime.now())
			score = evaluator.evaluate(builder, None, model, 0.7, 1.0)
			print 'Score evaluated by %s=%.2f' % (evaluator, score)
	print 'Ending run at %s' % datetime.now()

if __name__ == '__main__':
	main()