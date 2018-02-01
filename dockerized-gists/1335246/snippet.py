"""
L1-penalized minimization using the feature sign search algorithm.
"""

import logging
import numpy as np
log = logging.getLogger("feature_sign")
log.setLevel(logging.INFO)


def feature_sign_search(dictionary, signal, sparsity, solution=None):
    """
    Solve an L1-penalized minimization problem with the feature
    sign search algorithm of Lee et al (2006).

    Parameters
    ----------
    dictionary : array_like, 2-dimensional
        The dictionary of basis functions from which to form the
        sparse linear combination.

    signal : array_like, 1-dimensional
        The signal being decomposed as a sparse linear combination
        of the columns of the dictionary.

    sparsity : float
        The coefficient on the L1 penalty term of the cost function.

    solution : ndarray, 1-dimensional, optional
        Pre-allocated vector to use to store the solution.

    Returns
    -------
    solution : ndarray, 1-dimensional
        Vector containing the solution. If an array was passed in
        as the argument `solution`, it will be updated in place
        and the same object will be returned.

    References
    ----------
    .. [1] H. Lee, A. Battle, R. Raina, and A. Y. Ng. "Efficient
       sparse coding algorithms". Advances in Neural Information
       Processing Systems 19, 2007.
    """
    effective_zero = 1e-18
    # precompute matrices for speed.
    gram_matrix = np.dot(dictionary.T, dictionary)
    target_correlation = np.dot(dictionary.T, signal)
    # initialization goes here.
    if solution is None:
        solution = np.zeros(gram_matrix.shape[0])
    else:
        assert solution.ndim == 1, "solution must be 1-dimensional"
        assert solution.shape[0] == dictionary.shape[1], (
            "solution.shape[0] does not match dictionary.shape[1]"
        )
        # Initialize all elements to be zero.
        solution[...] = 0.
    signs = np.zeros(gram_matrix.shape[0], dtype=np.int8)
    active_set = set()
    z_opt = np.inf
    # Used to store max(abs(grad[nzidx] + sparsity * signs[nzidx])).
    # Set to 0 here to trigger a new feature activation on first iteration.
    nz_opt = 0
    # second term is zero on initialization.
    grad = - 2 * target_correlation  # + 2 * np.dot(gram_matrix, solution)
    max_grad_zero = np.argmax(np.abs(grad))
    # Just used to compute exact cost function.
    sds = np.dot(signal.T, signal)
    while z_opt > sparsity or not np.allclose(nz_opt, 0):
        if np.allclose(nz_opt, 0):
            candidate = np.argmax(np.abs(grad) * (signs == 0))
            log.debug("candidate feature: %d" % candidate)
            if grad[candidate] > sparsity:
                signs[candidate] = -1.
                solution[candidate] = 0.
                log.debug("added feature %d with negative sign" %
                          candidate)
                active_set.add(candidate)
            elif grad[candidate] < -sparsity:
                signs[candidate] = 1.
                solution[candidate] = 0.
                log.debug("added feature %d with positive sign" %
                          candidate)
                active_set.add(candidate)
            if len(active_set) == 0:
                break
        else:
            log.debug("Non-zero coefficient optimality not satisfied, "
                      "skipping new feature activation")
        indices = np.array(sorted(active_set))
        restr_gram = gram_matrix[np.ix_(indices, indices)]
        restr_corr = target_correlation[indices]
        restr_sign = signs[indices]
        rhs = restr_corr - sparsity * restr_sign / 2
        # TODO: implement footnote 3.
        #
        # If restr_gram becomes singular, check if rhs is in the column
        # space of restr_gram.
        #
        # If so, use the pseudoinverse instead; if not, update to first
        # zero-crossing along any direction in the null space of restr_gram
        # such that it has non-zero dot product with rhs (how to choose
        # this direction?).
        new_solution = np.linalg.solve(np.atleast_2d(restr_gram), rhs)
        new_signs = np.sign(new_solution)
        restr_oldsol = solution[indices]
        sign_flips = np.where(abs(new_signs - restr_sign) > 1)[0]
        if len(sign_flips) > 0:
            best_obj = np.inf
            best_curr = None
            best_curr = new_solution
            best_obj = (sds + (np.dot(new_solution,
                                      np.dot(restr_gram, new_solution))
                        - 2 * np.dot(new_solution, restr_corr))
                        + sparsity * abs(new_solution).sum())
            if log.isEnabledFor(logging.DEBUG):
                # Extra computation only done if the log-level is
                # sufficient.
                ocost = (sds + (np.dot(restr_oldsol,
                                       np.dot(restr_gram, restr_oldsol))
                        - 2 * np.dot(restr_oldsol, restr_corr))
                        + sparsity * abs(restr_oldsol).sum())
                cost = (sds + np.dot(new_solution,
                                     np.dot(restr_gram, new_solution))
                        - 2 * np.dot(new_solution, restr_corr)
                        + sparsity * abs(new_solution).sum())
                log.debug("Cost before linesearch (old)\t: %e" % ocost)
                log.debug("Cost before linesearch (new)\t: %e" % cost)
            else:
                ocost = None
            for idx in sign_flips:
                a = new_solution[idx]
                b = restr_oldsol[idx]
                prop = b / (b - a)
                curr = restr_oldsol - prop * (restr_oldsol - new_solution)
                cost = sds + (np.dot(curr, np.dot(restr_gram, curr))
                              - 2 * np.dot(curr, restr_corr)
                              + sparsity * abs(curr).sum())
                log.debug("Line search coefficient: %.5f cost = %e "
                          "zero-crossing coefficient's value = %e" %
                          (prop, cost, curr[idx]))
                if cost < best_obj:
                    best_obj = cost
                    best_prop = prop
                    best_curr = curr
            log.debug("Lowest cost after linesearch\t: %e" % best_obj)
            if ocost is not None:
                if ocost < best_obj and not np.allclose(ocost, best_obj):
                    log.debug("Warning: objective decreased from %e to %e" %
                              (ocost, best_obj))
        else:
            log.debug("No sign flips, not doing line search")
            best_curr = new_solution
        solution[indices] = best_curr
        zeros = indices[np.abs(solution[indices]) < effective_zero]
        solution[zeros] = 0.
        signs[indices] = np.int8(np.sign(solution[indices]))
        active_set.difference_update(zeros)
        grad = - 2 * target_correlation + 2 * np.dot(gram_matrix, solution)
        z_opt = np.max(abs(grad[signs == 0]))
        nz_opt = np.max(abs(grad[signs != 0] + sparsity * signs[signs != 0]))
    return solution
