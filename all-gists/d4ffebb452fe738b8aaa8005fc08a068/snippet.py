import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.cross_validation import StratifiedKFold
from sklearn.grid_search import GridSearchCV

class PUClassifier(object):
    def __init__(self, trad_clf=None, n_folds=2):
        self.trad_clf = trad_clf
        self.n_folds = n_folds

    def fit(self, X, s):
        if self.trad_clf is None:
            self.trad_clf = GridSearchCV(SGDClassifier(loss="log", penalty="l2"), param_grid={"alpha": np.logspace(-4, 0, 10)})

        c = np.zeros(self.n_folds)
        for i, (itr, ite) in enumerate(StratifiedKFold(s, n_folds=self.n_folds, shuffle=True)):
            self.trad_clf.fit(X[itr], s[itr])
            c[i] = self.trad_clf.predict_proba(X[ite][s[ite]==1])[:,1].mean()
        self.c = c.mean()
        return self

    def sample(self, X, s):
        if not hasattr(self, "c"):
            self.fit(X, s)
        X_positive = X[s==1]
        X_unlabeled = X[s==0]
        n_positive = X_positive.shape[0]
        n_unlabeled = X_unlabeled.shape[0]

        X_train = np.r_[X_positive, X_unlabeled, X_unlabeled]
        y_train = np.concatenate([np.repeat(1, n_positive), np.repeat(1, n_unlabeled), np.repeat(0, n_unlabeled)])

        self.trad_clf.fit(X, s)
        p_unlabeled = self.trad_clf.predict_proba(X_unlabeled)[:,1]
        w_positive = ((1 - self.c) / self.c) * (p_unlabeled / (1 - p_unlabeled))
        w_negative = 1 - w_positive
        sample_weight = np.concatenate([np.repeat(1.0, n_positive), w_positive, w_negative])
        return X_train, y_train, sample_weight

if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import itertools
    from sklearn import metrics
    np.random.seed(0)
    n_positive = 100
    n_negative = 500
    n = n_positive + n_negative
    mu1 = [0,0]
    mu2 = [2,2]
    Sigma1 = 0.1 * np.identity(2)
    Sigma2 = 0.5 * np.identity(2)
    X = np.r_[np.random.multivariate_normal(mu1, Sigma1, n_positive),
              np.random.multivariate_normal(mu2, Sigma2, n_negative)]
    y = np.concatenate([np.repeat(1, n_positive), np.repeat(0, n_negative)])
    n_unlabeled = int(n_positive * 0.7)
    s = y.copy()
    s[:n_unlabeled] = 0

    pu = PUClassifier(n_folds=5)
    X_train, y_train, sample_weight = pu.sample(X, s)
    alphas = np.logspace(-4, 0, 10)
    class_weights = [{1:1}]
    n_folds = 3
    best_score = -np.inf
    best_alpha = None
    best_class_weight = None
    for alpha, class_weight in itertools.product(alphas, class_weights):
        scores = np.zeros(n_folds)
        for i, (itr, ite) in enumerate(StratifiedKFold(y_train, n_folds=n_folds, shuffle=True)):
            clf = SGDClassifier(loss="hinge", penalty="l2", alpha=alpha, class_weight=class_weight).fit(X_train[itr], y_train[itr], sample_weight=sample_weight[itr])
            ypred = clf.predict(X_train[ite])
            scores[i] = metrics.accuracy_score(y_train[ite], ypred, sample_weight=sample_weight[ite])
        this_score = scores.mean()
        print alpha, class_weight, this_score
        if this_score > best_score:
            best_score = this_score
            best_alpha = alpha
            best_class_weight = class_weight

    print best_alpha, best_class_weight, best_score
    clf = SGDClassifier(loss="hinge", penalty="l2", alpha=best_alpha, class_weight=best_class_weight).fit(X_train, y_train, sample_weight=sample_weight)

    ypred = clf.predict(X[s==0])
    #ypred = pu.trad_clf.predict_proba(X[s==0])[:,1]>=0.5*pu.c # <- this can also be used. 
    trad_ypred = pu.trad_clf.predict(X[s==0])
    accuracy = metrics.accuracy_score(y[s==0], ypred)
    trad_accuracy = metrics.accuracy_score(y[s==0], trad_ypred)
    print "accuracy (traditional):", trad_accuracy
    print "accuracy (non-traditional):", accuracy

    # plot
    ypred = clf.predict(X)
    trad_ypred = pu.trad_clf.predict(X)
    offset = 1.0
    XX, YY = np.meshgrid(np.linspace(X[:,0].min()-offset,X[:,0].max()+offset,100),
                         np.linspace(X[:,1].min()-offset,X[:,1].max()+offset,100))
    Z = clf.decision_function(np.c_[XX.ravel(),YY.ravel()])
    Z = Z.reshape(XX.shape)

    plt.figure(figsize=(10, 10))
    plt.subplot(2, 2, 1)
    colors = ["r", "b"]
    plot_colors = [colors[yy] for yy in y==1]
    plt.scatter(X[:,0], X[:,1], s=50, color=plot_colors)
    plt.title("true")

    plt.subplot(2, 2, 2)
    colors = ["gray", "b"]
    plot_colors = [colors[ss] for ss in s]
    plt.scatter(X[:,0], X[:,1], s=50, color=plot_colors)
    plt.title("positive and unlabeled data")

    plt.subplot(2, 2, 3)
    colors = ["r", "b"]
    plot_colors = [colors[yy] for yy in trad_ypred]
    plt.scatter(X[:,0], X[:,1], s=50, color=plot_colors)
    plt.title("traditional (accuracy={})".format(trad_accuracy))

    plt.subplot(2, 2, 4)
    colors = ["r", "b"]
    plot_colors = [colors[yy] for yy in ypred]
    plt.contour(XX, YY, Z, levels=[0.0], colors="green")
    plt.scatter(X[:,0], X[:,1], s=50, color=plot_colors)
    plt.title("non-traditional (accuracy={})".format(accuracy))
    plt.tight_layout()
    plt.show()
    #plt.savefig("pusampler_demo.png")
