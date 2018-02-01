"""

http://en.wikipedia.org/wiki/ID3_algorithm
http://www.cise.ufl.edu/~ddd/cap6635/Fall-97/Short-papers/2.htm

"""

from collections import namedtuple, Counter, defaultdict
from math import log2


UNCLASSIFIED_VALUE = -99


class ID3Classifier(object):

    def __init__(self):
        self.root_node = None

    def fit(self, samples, target):
        """Create the decision tree."""

        training_samples = [TrainingSample(s, t)
                            for s, t in zip(samples, target)]
        predicting_features = list(range(len(samples[0])))
        self.root_node = self.create_decision_tree(training_samples,
                                                   predicting_features)

    def predict(self, X, allow_unclassified=False):
        default_klass = 1
        if allow_unclassified:
            default_klass = UNCLASSIFIED_VALUE
        predicted_klasses = []

        for sample in X:
            klass = None
            current_node = self.root_node
            while klass is None:
                if current_node.is_leaf():
                    klass = current_node.klass
                else:
                    key_value = sample[current_node.feature]
                    if key_value in current_node:
                        current_node = current_node[key_value]
                    else:
                        # UNCLASSIFIED_VALUE
                        klass = default_klass
            predicted_klasses.append(klass)
        return predicted_klasses

    def score(self, X, target, allow_unclassified=True):
        predicted = self.predict(X, allow_unclassified=allow_unclassified)
        n_matches = sum(p == t for p, t in zip(predicted, target))
        return 1.0 * n_matches / len(X)

    def create_decision_tree(self, training_samples, predicting_features):
        """Recursively, create a desition tree and return the parent node."""

        if not predicting_features:
            # No more predicting features
            default_klass = self.get_most_common_class(training_samples)
            root_node = DecisionTreeLeaf(default_klass)
        else:
            klasses = [sample.klass for sample in training_samples]
            if len(set(klasses)) == 1:
                target_klass = training_samples[0].klass
                root_node = DecisionTreeLeaf(target_klass)
            else:
                best_feature = self.select_best_feature(training_samples,
                                                        predicting_features,
                                                        klasses)
                # Create the node to return and create the sub-tree.
                root_node = DecisionTreeNode(best_feature)
                best_feature_values = {s.sample[best_feature]
                                       for s in training_samples}
                for value in best_feature_values:
                    samples = [s for s in training_samples
                               if s.sample[best_feature] == value]
                    # Recursively, create a child node.
                    child = self.create_decision_tree(samples,
                                                      predicting_features)
                    root_node[value] = child
        return root_node

    @staticmethod
    def get_most_common_class(trainning_samples):
        """Return the most common class in the given samples."""

        klasses = [s.klass for s in trainning_samples]
        counter = Counter(klasses)
        k, = counter.most_common(n=1)
        return k[0]

    def select_best_feature(self, samples, features, klasses):
        """
        Select, remove from list and return the feature that best classifies
        the samples.

        The best feature is the one with higher information gain for the
        provided samples (mimizes entropy in klasses).

        """
        gain_factors = [(self.information_gain(samples, feat, klasses), feat)
                        for feat in features]
        gain_factors.sort()
        best_feature = gain_factors[-1][1]
        features.pop(features.index(best_feature))
        return best_feature

    def information_gain(self, samples, feature, klasses):
        """
        Information gain is the measure of the difference in entropy from before
        to after the samples are split on the given feature values. In other
        words, how much uncertainty in the samples was reduced after splitting
        them on the given feature.

        """
        N = len(samples)
        samples_partition = defaultdict(list)
        for s in samples:
            samples_partition[s.sample[feature]].append(s)
        feature_entropy = 0.0
        for partition in samples_partition.values():
            sub_klasses = [s.klass for s in partition]
            feature_entropy += (len(partition) / N) * self.entropy(sub_klasses)

        return self.entropy(klasses) - feature_entropy

    @staticmethod
    def entropy(dataset):
        """Measure of the amount of uncertainty in the given dataset."""

        N = len(dataset)
        counter = Counter(dataset)
        return sum(-1.0*(counter[k] / N)*log2(counter[k] / N) for k in counter)


TrainingSample = namedtuple('TrainingSample', ('sample', 'klass'))


class DecisionTreeNode(dict):
    def __init__(self, feature, *args, **kwargs):
        self.feature = feature
        super(DecisionTreeNode, self).__init__(*args, **kwargs)

    def is_leaf(self):
        return False

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.feature)


class DecisionTreeLeaf(dict):
    def __init__(self, klass, *args, **kwargs):
        self.klass = klass
        super(DecisionTreeLeaf, self).__init__(*args, **kwargs)

    def is_leaf(self):
        return True

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.klass)
