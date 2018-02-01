results = []
for w in ['uniform', 'distance', lambda x: np.log(x)]:
    clf = KNeighborsClassifier(3, weights=w)
    w = str(w)
    clf.fit(train[features], train['high_quality'])
    preds = clf.predict(test[features])
    accuracy = np.where(preds==test['high_quality'], 1, 0).sum() / float(len(test))
    print "Weights: %s, Accuracy: %3f" % (w, accuracy)

    results.append([w, accuracy])

results = pd.DataFrame(results, columns=["weight_method", "accuracy"])
print results
#  weight_method  accuracy
# 0   uniform     0.797313
# 1  distance     0.816418
# 2       log     0.823284