# Mathieu Blondel, May 2012
# License: BSD 3 clause

import numpy as np

def euclidean_distances(X, Y=None, Y_norm_squared=None, squared=False):
    XX = np.sum(X * X, axis=1)[:, np.newaxis]
    YY = np.sum(Y ** 2, axis=1)[np.newaxis, :]
    distances = np.dot(X, Y.T)
    distances *= -2
    distances += XX
    distances += YY
    np.maximum(distances, 0, distances)

    if X is Y:
        # Ensure that distances between vectors and themselves are set to 0.0.
        # This may not be the case due to floating point rounding errors.
        distances.flat[::distances.shape[0] + 1] = 0.0

    return distances if squared else np.sqrt(distances)

class GaussianKernel(object):

    def __init__(self, gamma=1.0):
        self.gamma = gamma

    def compute(self, X, Y):
        K = euclidean_distances(X, Y, squared=True)
        K *= -self.gamma
        np.exp(K, K)    # exponentiate K in-place
        return K

class HingeLoss(object):

    def __init__(self, threshold=1):
        self.threshold = threshold # a.k.a geometrical margin

    def get_update(self, p, y):
        z = p * y
        if z <= self.threshold:
            return y
        return 0.0

class LogLoss(object):

    def get_update(self, p, y):
        z = p * y
        # approximately equal and saves the computation of the log
        if z > 18.0:
            return np.exp(-z) * y
        if z < -18.0:
            return y
        return y / (np.exp(z) + 1.0)

class SquaredLoss(object):

    def get_update(self, p, y):
        return -p + y

np.random.seed(0)

class KernelSGD(object):

    def __init__(self,
                 # Note: eta (learning rate) and lmbda (regularization) have no
                 # impact if loss=HingeLoss(threshold=0).
                 eta=1,
                 lmbda=0.01,
                 kernel=GaussianKernel(),
                 loss=HingeLoss(),
                 n_iter=1):
        self.eta = eta
        self.lmbda = lmbda
        self.kernel = kernel
        self.loss = loss
        self.n_iter = n_iter

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.alpha = np.zeros(n_samples, dtype=np.float64)

        # Gram matrix
        K = self.kernel.compute(X, X)

        for t in range(self.n_iter):
            for i in range(n_samples):
                pred = np.dot(K[:, i], self.alpha)
                # Update wrt to loss term.
                update = self.loss.get_update(pred, y[i])
                if update != 0:
                    self.alpha[i] += update * self.eta
                # Update wrt to regularization term.
                self.alpha *= (1 - self.eta * self.lmbda)

        # Support vectors
        sv = self.alpha != 0
        self.alpha = self.alpha[sv]
        self.sv = X[sv]
        print "%d support vectors out of %d points" % (len(self.alpha),
                                                       n_samples)

    def decision_function(self, X):
        K = self.kernel.compute(X, self.sv)
        return np.dot(K, self.alpha)

    def predict(self, X):
        return np.sign(self.decision_function(X))

if __name__ == "__main__":
    import pylab as pl

    def gen_non_lin_separable_data():
        mean1 = [-1, 2]
        mean2 = [1, -1]
        mean3 = [4, -4]
        mean4 = [-4, 4]
        cov = [[1.0,0.8], [0.8, 1.0]]
        X1 = np.random.multivariate_normal(mean1, cov, 50)
        X1 = np.vstack((X1, np.random.multivariate_normal(mean3, cov, 50)))
        y1 = np.ones(len(X1))
        X2 = np.random.multivariate_normal(mean2, cov, 50)
        X2 = np.vstack((X2, np.random.multivariate_normal(mean4, cov, 50)))
        y2 = np.ones(len(X2)) * -1
        return X1, y1, X2, y2

    def split_train(X1, y1, X2, y2):
        X1_train = X1[:90]
        y1_train = y1[:90]
        X2_train = X2[:90]
        y2_train = y2[:90]
        X_train = np.vstack((X1_train, X2_train))
        y_train = np.hstack((y1_train, y2_train))
        return X_train, y_train

    def split_test(X1, y1, X2, y2):
        X1_test = X1[90:]
        y1_test = y1[90:]
        X2_test = X2[90:]
        y2_test = y2[90:]
        X_test = np.vstack((X1_test, X2_test))
        y_test = np.hstack((y1_test, y2_test))
        return X_test, y_test

    def plot_contour(X1_train, X2_train, clf):
        pl.plot(X1_train[:,0], X1_train[:,1], "ro")
        pl.plot(X2_train[:,0], X2_train[:,1], "bo")
        pl.scatter(clf.sv[:,0], clf.sv[:,1], s=100, c="g")

        X1, X2 = np.meshgrid(np.linspace(-6,6,50), np.linspace(-6,6,50))
        X = np.array([[x1, x2] for x1, x2 in zip(np.ravel(X1), np.ravel(X2))])
        Z = clf.decision_function(X).reshape(X1.shape)
        pl.contour(X1, X2, Z, [0.0], colors='k', linewidths=1, origin='lower')

        pl.axis("tight")
        pl.show()

    def test():
        X1, y1, X2, y2 = gen_non_lin_separable_data()
        X_train, y_train = split_train(X1, y1, X2, y2)
        X_test, y_test = split_test(X1, y1, X2, y2)

        clf = KernelSGD(kernel=GaussianKernel(),
                        loss=HingeLoss(threshold=0),
                        n_iter=5)
        clf.fit(X_train, y_train)

        y_predict = clf.predict(X_test)
        correct = np.sum(y_predict == y_test)
        print "%d out of %d predictions correct" % (correct, len(y_predict))

        plot_contour(X_train[y_train==1], X_train[y_train==-1], clf)

    test()
