import collections
import numpy as np


class CompressedFeatures:

    def __init__(self, num_features=50):
        self.random_components = collections.defaultdict(
                self._generate_component)
        self.num_features = num_features
        self.reset_features()

    def _generate_component(self):
        """Internal method to generate a random vector on demand."""
        rv = np.random.randn(self.num_features, 1)
        rv /= np.sqrt(np.dot(rv.T, rv))  # normalize to unit length
        return rv

    def reset_features(self):
        self.feature_vector = np.zeros((self.num_features, 1))

    def get_features(self):
        return self.feature_vector[:, 0]

    def increment_component(self, component_key, scale=1.0):
        self.feature_vector += scale * self.random_components[component_key]


if __name__ == '__main__':
    # Example usage.

    # Optionally, seed the RNG if you want experiments to be repeatable.
    np.random.seed(909090)

    cf = CompressedFeatures(5)  # compress to 5 dimensions
    
    # Compute compressed features for User 1, provided her history.
    cf.reset_features()
    cf.increment_component(("addition exercise", "correct"))
    cf.increment_component(("calculus exercise", "incorrect"))
    print "User 1: ", cf.get_features()

    # Compute compressed features for User 2.
    cf.reset_features()
    cf.increment_component(("addition exercise", "correct"))
    cf.increment_component(("geometery exercise", "correct"))
    cf.increment_component(("calculus exercise", "correct"))
    print "User 2: ", cf.get_features()
