def splitData(df, trainPerc=0.6, cvPerc=0.2, testPerc=0.2):
    """
    return: training, cv, test
            (as pandas dataframes)
    params:
              df: pandas dataframe
       trainPerc: float | percentage of data for trainin set (default=0.6
          cvPerc: float | percentage of data for cross validation set (default=0.2)
        testPerc: float | percentage of data for test set (default=0.2)
                  (trainPerc + cvPerc + testPerc must equal 1.0)
    """
    assert trainPerc + cvPerc + testPerc == 1.0

    # create random list of indices
    from random import shuffle
    N = len(df)
    l = range(N)
    shuffle(l)

    # get splitting indicies
    trainLen = int(N*trainPerc)
    cvLen    = int(N*cvPerc)
    testLen  = int(N*testPerc)

    # get training, cv, and test sets
    training = df.ix[l[:trainLen]]
    cv       = df.ix[l[trainLen:trainLen+cvLen]]
    test     = df.ix[l[trainLen+cvLen:]]

    #print len(cl), len(training), len(cv), len(test)

    return training, cv, test


def getScore(df, classifier, classTitle, trainPerc, testPerc):
    """
    return: float | accuracy score for classification model (e[0,1])
    params:
               df: pandas dataframe
       classifier: sklearn classifier
       classTitle: string | title of class column in df
        trainPerc: percentage of data to train on (default=0.80)
         testPerc: percentage of data to test on (default=0.20)
                   (trainPerc + testPerc = 1.0)
    """
    assert trainPerc + testPerc == 1.0
    
    # split the dataset
    training, cv, test = splitData(df, trainPerc=trainPerc, cvPerc=0.00, testPerc=testPerc)
    
    # get the features and classes
    featureNames = [col for col in df.columns if col != classTitle]
    trainFeatures = training[ featureNames ].values
    trainClasses  = training[ classTitle   ].values
    
    # create class dict to track numeric classes
    classToString = {}
    classToNumber = {}
    for i, c in enumerate( sorted(set(trainClasses)) ):
        classToString[i] = c
        classToNumber[c] = i
    
    # change classes to numbers (if not already)
    trainClasses = [classToNumber[c] for c in trainClasses]
    
    # fit the model
    classifier.fit(trainFeatures, trainClasses)
    
    # formt cross validation set
    testFeatures = test[ featureNames ].values
    testClasses  = [classToNumber[c] for c in test[classTitle].values]
    
    # compute the score on the test set
    score = classifier.score(testFeatures, testClasses)
    
    return score


def testModel(df, classifier, classTitle, N=1, trainPerc=0.80, testPerc=0.20):
    """
    return: list[float] | list of scores for model (e[0,1])
    params:
           df: pandas dataframe
   classifier: sklearn classifier
   classTitle: string | title of class column in df
            N: int | number of tests to run (default=1)
    trainPerc: percentage of data to train on (default=0.80)
     testPerc: percentage of data to test on (default=0.20)
               (trainPerc + testPerc = 1.0)
    """
    # compute N scores
    scores = []
    for i in range(N):
        score = getScore(df=df, classifier=classifier, classTitle=classTitle, trainPerc=trainPerc, testPerc=testPerc)
        scores.append(score)
        
    return scores


