import pandas as pd
from sklearn import neighbors, datasets
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.metrics import  accuracy_score
from sklearn.preprocessing import Imputer
from sklearn.neighbors import KNeighborsClassifier
import pylab as p1
from matplotlib.colors import ListedColormap


"""Sam was here"""

df1 = pd.read_csv("/Users/samanrahbar/Desktop/knnDataSet.csv")

df1 = df1[['x', 'y', 'L']]

Xtrain = df1[['x', 'y']]
Ytrain = df1.L


X, xx, Y, yy = train_test_split(Xtrain, Ytrain, test_size =.25, random_state = 0, shuffle= True)

h = .01
knn = neighbors.KNeighborsClassifier(n_neighbors=1, weights='distance', algorithm= 'auto')

knn.fit(X,Y)

x_min, x_max = Xtrain['x'].min() - .5, Xtrain['x'].max() + .5
y_min, y_max = Xtrain['y'].min() - .5, Xtrain['y'].max() + .5

xmin, ymin = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

xmin = np.array(xmin)
ymin = np.array(ymin)


xx = np.array(xx)
yy = np.array(yy)


zc= knn.predict(np.c_[xmin.ravel(), ymin.ravel()])
zc = zc.reshape(xmin.shape)
z= knn.predict(xx)


plt.figure(1, figsize=(4, 3))
plt.set_cmap(plt.cm.Paired)
plt.pcolormesh(xmin, ymin, zc)

plt.scatter(Xtrain['x'], Xtrain['y'], c= Ytrain, marker = '+', s = 100)
plt.xlabel('X')
plt.ylabel('Y')

plt.xlim(xmin.min(), xmin.max())
plt.ylim(ymin.min(), ymin.max())

plt.xticks(())
plt.yticks(())

print("The Accuracy is:\n>>> "+ str(accuracy_score(yy, z)))
print('\n')
print("----------------------------------------\n The confussion matrix is as below:")
print('\n')
print(confusion_matrix(yy, z))

plt.show()


