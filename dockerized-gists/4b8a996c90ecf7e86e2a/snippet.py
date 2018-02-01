def Group(X, Y):
    temp = dict.fromkeys(X, [0, 0])
    L = range(len(X))

    for i in L:
        temp[X[i]][0] += Y[i]
        temp[X[i]][1] += 1
	    
    return temp


def Group2(X, Y):
    temp = {x : [0,0] for x in X}
    L = range(len(X))

    for i in L:
        temp[X[i]][0] += Y[i]
        temp[X[i]][1] += 1
	    
    return temp


def Group3(X, Y):
    temp = {x : [0,0] for x in X}

    for i,x in enumerate(X):
        temp[x][0] += Y[i]
        temp[x][1] += 1
	    
    return temp


def Group4(X, Y):
    import itertools
    data = sorted(zip(X,Y))
    query_return = dict()
    for key, values in itertools.groupby(data, key=lambda x: x[0]):
        summed_values = sum((x[1] for x in values))
        query_return[key] = summed_values

    return query_return
        


def Group5(X, Y):
    import itertools
    data = sorted(zip(X,Y))
    query_return = dict()
    for key, values in itertools.groupby(data, key=lambda x: x[0]):
        values = [x[1] for x in values]
        summed_values = sum(values)
        query_return[key] = (summed_values, len(values))

    return query_return
