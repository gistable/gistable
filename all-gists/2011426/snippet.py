import numpy as np
import scipy.stats


class ChineseRestaurantProcess(object):
    def __init__(self, alpha):
        self.alpha = alpha
        self.customers = []
    def sample(self, n_samples=1):
        samples = []
        for i in xrange(n_samples):
            probs = np.hstack([self.customers, self.alpha])
            probs /= probs.sum()
            table = np.where(np.random.multinomial(1, probs))[0][0]
            if table < len(self.customers):
                self.customers[table] += 1
            else:
                self.customers.append(1)
            samples.append(table)
            if len(samples) == 1:
                return samples[0]
        return samples

class WishartSampler(object):
    # Odell and Feiveson, 1966:  A numerical procedure to generate a sample covariance matrix
    def __init__(self, degrees_freedom, n_features):
        if degrees_freedom < n_features - 1:
            raise ValueError("Degrees of freedom must be bigger than n_features - 1")
        self.degrees_freedom = degrees_freedom
        self.n_features = n_features
    def sample(self, n_samples=1):
        samples = []
        inds = np.arange(self.n_features)
        for i in xrange(n_samples):
            V = [np.random.chisquare(self.degrees_freedom - k + 1)
                    for k in xrange(self.n_features)]
            V = np.array(V)
            N = np.random.normal(size=(self.n_features, self.n_features))
            N = np.triu(N, 1)
            diag = V + np.sum(N ** 2, axis=0)
            B = N * np.sqrt(V) + np.dot(N.T, N)
            B = np.triu(B, 1)
            B += B.T
            B[inds, inds] = diag
            samples.append(B)
        if len(samples) == 1:
            return samples[0]
        return samples

class MultiVariateGaussian(object):
    def __init__(self, mean, covariance):
        self.mean = mean
        self.covariance = covariance
    def sample(self, n_samples=1):
        samples = np.random.multivariate_normal(mean=self.mean,
                cov=self.covariance, size=n_samples)
        return samples


class DPGMMSampler(object):
    def __init__(self, alpha, degrees_freedoms, sigma, n_features):
        self.alpha = alpha
        self.n_features = n_features
        self.deg_freedoms = degrees_freedoms
        self.sigma = sigma
        self.crp = ChineseRestaurantProcess(alpha)
        self.wishart = WishartSampler(degrees_freedoms, n_features)
        self.gaussian_prior = scipy.stats.norm(scale=self.sigma)
        self.gaussians = []
    def sample(self, n_samples):
        samples = []
        for i in xrange(n_samples):
            cluster = self.crp.sample()
            if cluster >= len(self.gaussians):
                mean = self.gaussian_prior.rvs(size=self.n_features)
                covariance = np.linalg.inv(self.wishart.sample())
                self.gaussians.append(MultiVariateGaussian(mean, covariance))
            samples.append(self.gaussians[cluster].sample())
        return np.vstack(samples)


def test_crp():
    crp = ChineseRestaurantProcess(.5)
    print(crp.sample(10))

def test_wishart():
    wishart = WishartSampler(6, 4)
    print(wishart.sample())


def test_dpgmm():
    import matplotlib.pyplot as plt
    dpgmm = DPGMMSampler(10.1, 10, 3, 2)
    X = dpgmm.sample(100)
    plt.scatter(X[:, 0], X[:, 1], c='b')
    for g in dpgmm.gaussians:
        plt.plot(g.mean[0], g.mean[1], 'r.')
    plt.show()

if __name__ == "__main__":
    #test_crp()
    #test_wishart()
    test_dpgmm()
