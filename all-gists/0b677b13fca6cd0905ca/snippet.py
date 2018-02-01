import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import fetch_olivetti_faces
from sklearn.utils.validation import check_random_state
from scipy.ndimage import imread

from sklearn.ensemble import ExtraTreesRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import RidgeCV
from compiler.ast import flatten
from matplotlib.pyplot import title

# Load the faces datasets
data = fetch_olivetti_faces()
targets = data.target

#Load my face
my_face = imread(fname='me.gif', flatten = True)
my_normalized_face = my_face / 255.0
my_flattened_normalized_face = np.ndarray(4096)
for i, row in enumerate(my_normalized_face):
    for j, pixel in enumerate(row):
        my_flattened_normalized_face[i * 64 + j] = pixel

data = data.images.reshape((len(data.images), -1))
my_face_data = my_normalized_face.reshape((len(my_normalized_face), -1))

train = data[targets]
test = data[targets >= 30]  # Test on independent people

# Test on a subset of people
n_faces = 4
rng = check_random_state(5)
face_ids = rng.randint(test.shape[0], size=(n_faces, ))
test = test[face_ids, :]

n_pixels = data.shape[1]
X_train = train[:, :int(np.ceil(0.5 * n_pixels) )]  # Upper half of the faces
y_train = train[:, int(np.floor(0.5 * n_pixels)):]  # Lower half of the faces
X_test = test[:, :int(np.ceil(0.5 * n_pixels) )]
y_test = test[:, int (np.floor(0.5 * n_pixels)): ]

X_my_face_test = my_flattened_normalized_face[:int(np.ceil(0.5 * n_pixels))]
Y_my_face_test = my_flattened_normalized_face[int(np.floor(0.5 * n_pixels)):]                                         

# Fit estimators
ESTIMATORS = {
    "Extra trees": ExtraTreesRegressor(n_estimators=15, max_features=20,
                                       random_state=3),
    "K-nn": KNeighborsRegressor(),
#    These classifiers don't seem to work.
#    "Linear regression": LinearRegression(),
#    "Ridge": RidgeCV(),
}

y_test_predict = dict()
my_face_y_test_predict = dict()
for name, estimator in ESTIMATORS.items():
    estimator.fit(X_train, y_train)
    y_test_predict[name] = estimator.predict(X_test)
    my_face_y_test_predict[name] = estimator.predict(X_my_face_test)

# Plot the completed faces
image_shape = (64, 64)

n_cols = 1 + len(ESTIMATORS)
plt.figure(figsize=(2. * n_cols, 2.26 * 2.0))
plt.suptitle("Face completion with multi-output estimators", size=16)

#Plot my face
my_true_face = np.hstack((X_my_face_test, Y_my_face_test))

#Print the top (true) part of my face for all faces)
sub = plt.subplot(1, n_cols, 1, title='Actual Face')
    
sub.axis("off")
sub.imshow(my_true_face.reshape(image_shape), cmap=plt.cm.gray, interpolation="nearest")

#Print the bottom (estimated) part of my face for all faces
for j, est in enumerate(sorted(ESTIMATORS)):
    my_completed_face = np.hstack((X_my_face_test, my_face_y_test_predict[est][0]))   
    sub = plt.subplot(1, n_cols, j + 2, title=est)

    sub.axis("off")
    try:
        sub.imshow(my_completed_face.reshape(image_shape), cmap=plt.cm.gray, interpolation="nearest")
    except ValueError:
        continue

plt.show()
