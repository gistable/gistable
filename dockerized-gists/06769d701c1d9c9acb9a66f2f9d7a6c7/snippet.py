import numpy as np


def xgb_quantile_eval(preds, dmatrix, quantile=0.2):
    """
    Customized evaluational metric that equals
    to quantile regression loss (also known as
    pinball loss).

    Quantile regression is regression that
    estimates a specified quantile of target's
    distribution conditional on given features.

    @type preds: numpy.ndarray
    @type dmatrix: xgboost.DMatrix
    @type quantile: float
    @rtype: float
    """
    labels = dmatrix.get_label()
    return ('q{}_loss'.format(quantile),
            np.nanmean((preds >= labels) * (1 - quantile) * (preds - labels) +
                       (preds < labels) * quantile * (labels - preds)))


def xgb_quantile_obj(preds, dmatrix, quantile=0.2):
    """
    Computes first-order derivative of quantile
    regression loss and a non-degenerate
    substitute for second-order derivative.

    Substitute is returned instead of zeros,
    because XGBoost requires non-zero
    second-order derivatives. See this page:
    https://github.com/dmlc/xgboost/issues/1825
    to see why it is possible to use this trick.
    However, be sure that hyperparameter named
    `max_delta_step` is small enough to satisfy:
    ```0.5 * max_delta_step <=
       min(quantile, 1 - quantile)```.

    @type preds: numpy.ndarray
    @type dmatrix: xgboost.DMatrix
    @type quantile: float
    @rtype: tuple(numpy.ndarray)
    """
    try:
        assert 0 <= quantile <= 1
    except AssertionError:
        raise ValueError("Quantile value must be float between 0 and 1.")

    labels = dmatrix.get_label()
    errors = preds - labels

    left_mask = errors < 0
    right_mask = errors > 0

    grad = -quantile * left_mask + (1 - quantile) * right_mask
    hess = np.ones_like(preds)

    return grad, hess


# Example of usage:
# bst = xgb.train(hyperparams, train, num_rounds,
#                 obj=xgb_quantile_obj, feval=xgb_quantile_eval)
