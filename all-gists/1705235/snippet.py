import numpy as np

from IPython.parallel import Client

from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import KFold
from sklearn.svm import SVC
from sklearn import datasets
from sklearn.preprocessing import Scaler
from sklearn.utils import shuffle

digits = datasets.fetch_mldata("MNIST original")
X, y = digits.data, digits.target

X, y = shuffle(X, y)

X = Scaler().fit_transform(X)

params = dict(C=10. ** np.arange(-3, 3), gamma=10. ** np.arange(-3, 3))

rc = Client(profile='sge')
view = rc.load_balanced_view()


grid = GridSearchCV(SVC(), param_grid=params, cv=KFold(len(y), 4), n_jobs=view)

grid.fit(X, y)
print(grid.grid_scores_)
