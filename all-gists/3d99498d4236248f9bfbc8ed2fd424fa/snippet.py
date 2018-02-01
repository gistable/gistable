# This is an example of how to do stacking with H2O in Python


import h2o
from h2o.estimators.gbm import H2OGradientBoostingEstimator
from h2o.estimators.deeplearning import H2ODeepLearningEstimator
from h2o.estimators.glm import H2OGeneralizedLinearEstimator
from h2o.estimators.random_forest import H2ORandomForestEstimator
from sklearn import metrics  #will be replaced with ensemble_performance later


def source_stack_utils():
	'''
	Current location of h2o stack python utils
	'''
	import urllib
	url = "https://gist.githubusercontent.com/ledell/8ba8d064ae13169a1821faac70d2211b/raw/7d0fa741df619d1a5340e06258a91831951be8a9/stack.py"
	urllib.urlretrieve(url, "stack.py")
	

def prep_data_example():

	# Import a sample binary outcome train/test set into R
	train = h2o.import_file("http://www.stat.berkeley.edu/~ledell/data/higgs_10k.csv")
	test = h2o.import_file("http://www.stat.berkeley.edu/~ledell/data/higgs_test_5k.csv")
	y = "C1"
	x = list(train.columns)
	x.pop(0)

	family = "binomial"

	#For binary classification, response should be a factor
	train[y] = train[y].asfactor()  
	test[y] = test[y].asfactor()
	
	return x, y, train, test, family


def cvtrain_base_models(x, y, train, family):
	''' 
	Here we (5-fold) cross-validate a collection of base models
	This is an example of an ensemble of nine models:
	- 3 GBM
	- 3 DL
	- 2 RF
	- 1 GLM
	'''

	# All models must use exact same CV folds
	nfolds = 5
	fold_assignment = 'Modulo'


	# TO DO: Sync up family and distribution and un-hardcode distribution below
	gbm1 = H2OGradientBoostingEstimator(distribution='bernoulli',
	                                    ntrees=100,
	                                    max_depth=4,
	                                    learn_rate=0.1,
	                                    nfolds=nfolds,
	                                    fold_assignment=fold_assignment,
	                                    keep_cross_validation_predictions=True)

	gbm2 = H2OGradientBoostingEstimator(distribution='bernoulli',
	                                    ntrees=100,
	                                    max_depth=4,
	                                    learn_rate=0.1,
	                                    col_sample_rate=0.7,
	                                    nfolds=nfolds,
	                                    fold_assignment=fold_assignment,
	                                    keep_cross_validation_predictions=True)

	gbm3 = H2OGradientBoostingEstimator(distribution='bernoulli',
	                                    ntrees=100,
	                                    max_depth=2,
	                                    learn_rate=0.1,
	                                    nfolds=nfolds,
	                                    fold_assignment=fold_assignment,
	                                    keep_cross_validation_predictions=True)

	dl1 = H2ODeepLearningEstimator(distribution='bernoulli',
	                               activation='Rectifier', 
	                               hidden=[50,50,50],
	                               l1=1e-5, 
	                               epochs=10,
	                               nfolds=nfolds,
	                               fold_assignment=fold_assignment,
	                               keep_cross_validation_predictions=True)

	dl2 = H2ODeepLearningEstimator(distribution='bernoulli',
	                               activation='RectifierWithDropout', 
	                               hidden=[100,100,100],
	                               input_dropout_ratio=0.2, 
	                               l1=1e-5, 
	                               epochs=10,
	                               nfolds=nfolds,
	                               fold_assignment=fold_assignment,
	                               keep_cross_validation_predictions=True)

	dl3 = H2ODeepLearningEstimator(distribution='bernoulli',
	                               activation='Rectifier', 
	                               hidden=[200,200],
	                               l1=1e-6, 
	                               epochs=10,
	                               nfolds=nfolds,
	                               fold_assignment=fold_assignment,
	                               keep_cross_validation_predictions=True)

	rf1 = H2ORandomForestEstimator(#distribution='bernoulli',
	                               ntrees=300, 
	                               nfolds=nfolds,
	                               fold_assignment=fold_assignment,
	                               keep_cross_validation_predictions=True)

	rf2 = H2ORandomForestEstimator(#distribution='bernoulli',
	                               ntrees=300,
	                               sample_rate=0.7,
	                               mtries=10, 
	                               nfolds=nfolds,
	                               fold_assignment=fold_assignment,
	                               keep_cross_validation_predictions=True)

	glm1 = H2OGeneralizedLinearEstimator(family='binomial',
	                                     nfolds=nfolds,
	                                     fold_assignment=fold_assignment,
	                                     keep_cross_validation_predictions=True)

	# Edit this list of base models to make different ensembles
	models = [gbm1, gbm2, gbm3, dl1, dl2, dl3, rf1, rf2, glm1]

	for model in models:
		model.train(x=x, y=y, training_frame=train)

	return models



def main():

	h2o.init()

	# Load some example binary response data
	x, y, train, test, family = prep_data_example()
	
	# Load stacking utils
	source_stack_utils()
	from stack import make_Z, get_cvpreds, stack, metapredict

	# Cross-validation & training of base models
	# Above we train an abitrary assortment of base models
	models = cvtrain_base_models(x=x, y=y, train=train, family=family)

	# Define a NN-GLM metalearner
	metalearner = H2OGeneralizedLinearEstimator(family='binomial', non_negative=True)

	# Fit the stacked ensemble / Super Learner
	metafit = stack(models=models, 
			metalearner=metalearner,
			response_frame=train[y],
			seed=1,
			keep_levelone_data=True)

	# Generate ensemble prediction on the test set
	pred, basepred = metapredict(models=models, metafit=metafit, test_data=test)

	# TO DO: Add metafit.ensemble_performance()
	# Evaluate ensemble test performance
	preds = pred[2].as_data_frame(True)
	labels = test[y].as_data_frame(True)
	fpr, tpr, thresholds = metrics.roc_curve(labels, preds, pos_label=1)
	auc = metrics.auc(fpr, tpr)
	print str(auc) + "  " + "H2O Ensemble" 

	# Evaluate base learner test set performance (for comparison)
	for model in models:
		bperf = model.model_performance(test_data=test)
		print str(bperf.auc()) + "  " + model.model_id

	# 0.792100100148  H2O Ensemble
	# 0.781849246474  GBM_model_python_1471654758738_1
	# 0.782052358716  GBM_model_python_1471654758738_816
	# 0.769195957061  GBM_model_python_1471654758738_1837
	# 0.729095165124  DeepLearning_model_python_1471654758738_3028
	# 0.691393671746  DeepLearning_model_python_1471654758738_3057
	# 0.724608757556  DeepLearning_model_python_1471654758738_3086
	# 0.78333120166  DRF_model_python_1471654758738_3115
	# 0.787051172219  DRF_model_python_1471654758738_3896
	# 0.687091955549  GLM_model_python_1471654758738_4639

	# In this example, ensemble test AUC was 0.792 and the top base learner was 0.783