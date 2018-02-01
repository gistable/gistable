import numpy as np
import matplotlib.pyplot as plt
from numpy import random
import seaborn as sns
from sklearn import metrics
from puwrapper import PUWrapper
from sklearn.linear_model import LogisticRegression,LogisticRegressionCV
sns.set_style("white")
random.seed(0)

n1=100; n2=500; n=n1+n2;
mu1=[0,0]; mu2=[2,2]; Sigma1=0.1*np.identity(2); Sigma2=0.5*np.identity(2);
X=np.r_[random.multivariate_normal(mu1,Sigma1,n1),
        random.multivariate_normal(mu2,Sigma2,n2)]
y=np.concatenate([np.repeat(1,n1),np.repeat(0,n2)])

s=np.zeros(n,dtype=np.int32)
idxp=np.arange(n)[y==1][:np.int32(n1*0.3)]
s[idxp]=1
idx=random.permutation(n); X=X[idx]; y=y[idx]; s=s[idx];

# now s[i] indicates X[i] is positive or unlabeled

score=lambda l1,l2: metrics.f1_score(l1,l2,average=None)[1]
scorer=metrics.make_scorer(score)

from rbfmodel_wrapper import RbfModelWrapper
from sklearn.grid_search import GridSearchCV
Xce=X[np.random.permutation(len(X))[:100]]

base1=GridSearchCV(RbfModelWrapper(LogisticRegression(),Xce=Xce),param_grid={"gamma":np.logspace(-1,1,6)},scoring=scorer)
base2=GridSearchCV(RbfModelWrapper(LogisticRegression(),Xce=Xce),param_grid={"gamma":np.logspace(-1,1,6)},scoring=scorer)

clf=PUWrapper(base1).fit(X,s)
trad_clf=base2.fit(X,s)
print "accuracy (PU):",metrics.accuracy_score(y[s==0],clf.predict(X[s==0]))
print "pos's F1 (PU):",score(y[s==0],clf.predict(X[s==0]))

offset=.5
xx,yy=np.meshgrid(np.linspace(X[:,0].min()-offset,X[:,0].max()+offset,100),
                  np.linspace(X[:,1].min()-offset,X[:,1].max()+offset,100))

label=trad_clf.predict(X)
proba=trad_clf.predict_proba(np.c_[xx.ravel(),yy.ravel()])
Z=proba[:,1]
Z=Z.reshape(xx.shape)

label2=clf.predict(X)
proba=clf.predict_proba(np.c_[xx.ravel(),yy.ravel()])
Z2=proba[:,1]
Z2=Z2.reshape(xx.shape)

"""
b1=plt.scatter(X[s==1][:,0],X[s==1][:,1],c="blue",s=50)
b2=plt.scatter(X[s==0][:,0],X[s==0][:,1],c="grey",s=50)
plt.axis("tight")
plt.xlim((X[:,0].min()-offset,X[:,0].max()+offset))
plt.ylim((X[:,1].min()-offset,X[:,1].max()+offset))
plt.legend([b1,b2],
           ["positive","unlabeled"],
           prop={"size":10},loc="upper left")
plt.title("Positive and unlabeled data")
plt.tight_layout()
plt.show()
"""

"""
b1=plt.scatter(X[y==1][:,0],X[y==1][:,1],c="blue",s=50)
b2=plt.scatter(X[y==0][:,0],X[y==0][:,1],c="red",s=50)
plt.axis("tight")
plt.xlim((X[:,0].min()-offset,X[:,0].max()+offset))
plt.ylim((X[:,1].min()-offset,X[:,1].max()+offset))
plt.legend([b1,b2],
           ["positive","negative"],
           prop={"size":10},loc="upper left")
plt.title("Samples with true label")
plt.tight_layout()
plt.show()
"""

"""
a1=plt.contour(xx, yy, Z2, levels=[0.5], linewidths=2, colors='green')
b1=plt.scatter(X[label==1][:,0],X[label==1][:,1],c="blue",s=50)
b2=plt.scatter(X[label==0][:,0],X[label==0][:,1],c="red",s=50)
plt.axis("tight")
plt.xlim((X[:,0].min()-offset,X[:,0].max()+offset))
plt.ylim((X[:,1].min()-offset,X[:,1].max()+offset))
plt.legend([a1.collections[0],b1,b2],
           ["decision boundary","positive","negative"],
           prop={"size":10},loc="upper left")
plt.title("Result of traditional classification")
plt.tight_layout()
plt.savefig("result_of_tradclf.png")
plt.show()
"""


a1=plt.contour(xx, yy, Z2, levels=[0.5*clf.c_], linewidths=2, colors='green')
b1=plt.scatter(X[label2==1][:,0],X[label2==1][:,1],c="blue",s=50)
b2=plt.scatter(X[label2==0][:,0],X[label2==0][:,1],c="red",s=50)
plt.axis("tight")
plt.xlim((X[:,0].min()-offset,X[:,0].max()+offset))
plt.ylim((X[:,1].min()-offset,X[:,1].max()+offset))
plt.legend([a1.collections[0],b1,b2],
           ["decision boundary","positive","negative"],
           prop={"size":10},loc="upper left")
plt.title("Result of PU classification")
plt.tight_layout()
plt.show()

