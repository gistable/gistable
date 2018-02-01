import keras.backend as K

def FScore2(y_true, y_pred):
    '''
    The F score, beta=2
    '''
    B2 = K.variable(4)
    OnePlusB2 = K.variable(5)
    pred = K.round(y_pred)
    tp = K.sum(K.cast(K.less(K.abs(pred - K.clip(y_true, .5, 1.)), 0.01), 'float32'), -1)
    fp = K.sum(K.cast(K.greater(pred - y_true, 0.1), 'float32'), -1)
    fn = K.sum(K.cast(K.less(pred - y_true, -0.1), 'float32'), -1)

    f2 = OnePlusB2 * tp / (OnePlusB2 * tp + B2 * fn + fp)

    return K.mean(f2)

def FScore2_python(y_true, y_pred):
    '''
    python implementation of F_B Score, B=2
    # Inputs
        y_true: list of lists of 'true' values
        y_pred: list of lists of predicted values
    # Outputs
        returns the average F score
    '''
    B = 2
    B2 = B ** 2
    OnePlusB2 = 1 + B2
    FScore = []

    for i, true in enumerate(y_true):
        true = [int(category) for category in true]
        pred = [int(round(category)) for category in y_pred[i]]

        true_positives = 0
        false_positives = 0
        false_negatives = 0
        for j, true_cat in enumerate(true):
            if true_cat == 1:
                if y_pred[i][j] == 1:
                    true_positives += 1
                else:
                    false_negatives += 1
            elif y_pred[i][j] == 1:
                false_positives += 1

        _fscore = OnePlusB2 * true_positives / (OnePlusB2 * true_positives + B2 * false_negatives + false_positives)
        FScore.append(_fscore)

    avg = 0
    n = len(FScore)
    for score in FScore:
        avg += score/n

    return avg

def test_FScore2():
    '''test for FScore2'''
    # Test 1:
    y_true = [[1, 0, 0, 1],
              [0, 1, 0, 1]]
    y_pred = [[1, 1, 1, 1],
              [1, 0, 1, 1]]

    score_python = FScore2_python(y_true, y_pred)

    y_true = K.constant(y_true)
    y_pred = K.constant(y_pred)
    score_keras = K.eval(FScore2(y_true, y_pred))
    print('python:', score_python)
    print('keras:', score_keras)
    assert(abs(score_keras-score_python) < 0.0001)
    print('Test 1 passed!')

if __name__ == "__main__":
    test_FScore2()