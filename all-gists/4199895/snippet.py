try:
    import cPickle as pickle
except:
    import pickle
    
from sklearn.ensemble import RandomForestClassifier
import logging, os


class Lexent_classifier_sub:
    
    def __init__(self):
        sub_model_file = os.path.join(os.path.dirname(__file__), 'classifier_models/sub_model.p')
        training_file = open(sub_model_file)
        training_data = pickle.load(training_file)
        training_file.close()
        sub_target_file = os.path.join(os.path.dirname(__file__), 'classifier_models/sub_targets.p')
        targets_file = open(sub_target_file)
        targets = pickle.load(targets_file)
        targets_file.close()
        logging.info('Training with %s examples', len(training_data))

        self.clf = RandomForestClassifier() 
        self.clf = self.clf.fit(training_data, targets)


    def predict(self, feature_vector):
        predicted = self.clf.predict(feature_vector)
        logging.info('Prediction: %s', predicted)
        return predicted