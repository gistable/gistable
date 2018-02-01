In [1]: %paste
from sklearn.datasets import load_iris
from sklearn import tree
import coremltools

iris = load_iris()
clf = tree.DecisionTreeClassifier()
clf = clf.fit(iris.data, iris.target)

## -- End pasted text --

In [2]: coremltools.converters.sklearn.convert(clf)
Out[2]: 
input {
  name: "input"
  type {
    multiArrayType {
      shape: 4
    }
  }
}
output {
  name: "classLabel"
  type {
    int64Type {
    }
  }
}
output {
  name: "classProbability"
  type {
    dictionaryType {
      int64KeyType {
      }
    }
  }
}
predictedFeatureName: "classLabel"
predictedProbabilitiesName: "classProbability"