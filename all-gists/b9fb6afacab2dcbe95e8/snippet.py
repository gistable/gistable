%matplotlib inline
import matplotlib
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
plays = pd.read_table("usersha1-artmbid-artname-plays-sample.tsv", usecols=[0, 2, 3], names=['user', 'artist', 'plays'])
users = pd.read_table("usersha1-profile-sample.tsv", usecols=[0, 1], names=['user', 'gender'])

users=users.dropna()
genders=pd.get_dummies(users['gender'])
users=users.join(genders)

#top_artists=plays.groupby('artist').size().order(ascending=False)[:50]
artists=plays.groupby('artist').size()
top_artists=artists[artists>3600]
#top_plays = plays[plays['artist'].isin(top_artists.index)]
#some odd duplicates needed tidying up
top_plays = plays[plays['artist'].isin(top_artists.index)].groupby(['user','artist']).agg({'plays':np.max}).reset_index()

top_plays_t=top_plays.pivot('user', 'artist', 'plays').fillna(0)
to_model=pd.merge(users, top_plays_t, left_on='user', right_index=True, how='left').fillna(0)

Y=to_model['m'].values
X=to_model[(to_model.columns.values[4:])].values

from sklearn.preprocessing import StandardScaler
SS=StandardScaler()
XS=SS.fit_transform(X)

from sklearn.decomposition import PCA
pca = PCA(n_components=20)
pca_fit=pca.fit_transform(XS)
print(pca.explained_variance_ratio_)

from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, mean_squared_error, confusion_matrix
from sklearn.cross_validation import train_test_split
 
X_train, X_test, y_train, y_test = train_test_split(pca_fit, Y, test_size=0.33, random_state=0)
X_train2, X_cv, y_train2, y_cv = train_test_split(X_train, y_train, test_size=0.5, random_state=0)
 
knn_result=pd.DataFrame(columns=['Model', 'CP','Value','MSE','Accuracy', 'Precision'])
for k in range(1,21):
    neigh = KNeighborsClassifier(n_neighbors=k)
    neigh.fit(X_train2, y_train2)
    predict=neigh.predict(X_cv)
    mse=mean_squared_error(y_cv, predict)
    conf=confusion_matrix(y_cv, predict)
    accuracy=accuracy_score(y_cv, predict)
    precision=precision_score(y_cv, predict)
    knn_result.loc[k] = pd.Series({'Model': 'KNN','CP':'K', 'Value':k, 'MSE':mse, 'Accuracy':accuracy, 'Precision':precision})
    #print "%sNN - MSE: %s ACCURACY: %s PRECISION: %s" % (k, mse, accuracy, precision)
print knn_result

tree_result=pd.DataFrame(columns=['Model', 'CP','Value','MSE','Accuracy', 'Precision'])
for depth in range(1,21):
    tree = DecisionTreeClassifier(max_depth=depth)
    tree.fit(X_train2, y_train2)
    predict=tree.predict(X_cv)
    mse=mean_squared_error(y_cv, predict)
    conf=confusion_matrix(y_cv, predict)
    accuracy=accuracy_score(y_cv, predict)
    precision=precision_score(y_cv, predict)
    tree_result.loc[depth] = pd.Series({'Model': 'Tree','CP':'Max Depth', 'Value':depth, 'MSE':mse, 'Accuracy':accuracy, 'Precision':precision})
    #print "%sNN - MSE: %s ACCURACY: %s PRECISION: %s" % (k, mse, accuracy, precision)
	
forest_result=pd.DataFrame(columns=['Model', 'CP','Value','MSE','Accuracy', 'Precision'])
for d in range(1,21):
    RFC = RandomForestClassifier(n_estimators=5, max_depth=d)
    RFC.fit(X_train2, y_train2)
    predict=RFC.predict(X_cv)
    mse=mean_squared_error(y_cv, predict)
    conf=confusion_matrix(y_cv, predict)
    accuracy=accuracy_score(y_cv, predict)
    precision=precision_score(y_cv, predict)
    forest_result.loc[d] = pd.Series({'Model': 'Forest','CP':'Depth', 'Value':d, 'MSE':mse, 'Accuracy':accuracy, 'Precision':precision})
    #print "%sNN - MSE: %s ACCURACY: %s PRECISION: %s" % (k, mse, accuracy, precision)	

 
 
final_output=pd.concat([knn_result,tree_result, forest_result])
print final_output

#Visualize the results
#Grouped Line Plot
groups = final_output.groupby('Model')
# Plot
fig, (ax1,ax2,ax3) = plt.subplots(1,3, figsize=(15,5))

#fig=plt.figure(figsize=(10,10))
#ax1=fig.add_subplot(2,2,1)
#ax2=fig.add_subplot(2,2,2)
#ax3=fig.add_subplot(2,2,3)

for name, group in groups:
    ax1.plot(group.Value, group.MSE, linestyle='-',linewidth=2, label=name)
    ax2.plot(group.Value, group.Accuracy, linestyle='-',linewidth=2,  label=name)
    ax3.plot(group.Value, group.Precision, linestyle='-',linewidth=2,  label=name)
ax1.set_title('MSE')
ax2.set_title('Accuracy')
ax3.set_title('Precision')
ax1.legend(loc='best')

plt.show()

#Individual Scatter Plots
final_output[final_output['Model']=='Tree'].plot(x='Value', y='MSE', color='Orange', marker='o', linestyle='dashed', label='Tree - Depth', figsize=(8,5)).legend().set_visible(False)
final_output[final_output['Model']=='Forest'].plot( x='Value', y='MSE', color='Orange', marker='o', linestyle='dashed', label='Forest - n items', figsize=(8,5)).legend().set_visible(False)
final_output[final_output['Model']=='KNN'].plot( x='Value', y='MSE', color='Orange', marker='o', linestyle='dashed', label='KNN - K', figsize=(8,5)).legend().set_visible(False)

#build final model
RFC = RandomForestClassifier(n_estimators=5, max_depth=10)
RFC.fit(X_train, y_train)
predict=RFC.predict(X_test)
mse=mean_squared_error(y_test, predict)
conf=confusion_matrix(y_test, predict)
accuracy=accuracy_score(y_test, predict)
precision=precision_score(y_test, predict)

print "Final RF Model - MSE: %s ACCURACY: %s PRECISION: %s" % (mse, accuracy, precision)	


