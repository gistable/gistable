from sklearn.externals import joblib
import time
import numpy
import pickle

bigarray = numpy.zeros([190,91,190])
bigarray = bigarray.flatten()


### Saving
start = time.time()
joblib.dump(bigarray,"bigarray1.pkl")
end = time.time() - start
end
# 0.31264686584472656

start = time.time()
pickle.dump(bigarray,open("bigarray2.pkl","wb"))
end = time.time()-start
end
# 4.827500104904175

### Loading
start = time.time()
joblib.load("bigarray1.pkl")
end = time.time() - start
end
# 0.47748589515686035


start = time.time()
pickle.load(open("bigarray2.pkl","rb"))
end = time.time()-start
end
# 0.7575929164886475