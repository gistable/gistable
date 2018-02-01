from cvxopt import matrix as cvxmat, sparse, spmatrix
from cvxopt.solvers import qp, options
import numpy as np

def quadprog(H, f, Aeq, beq, lb, ub):
    """
    minimize:
            (1/2)*x'*H*x + f'*x
    subject to:
            Aeq*x = beq 
            lb <= x <= ub
    """
    P, q, G, h, A, b = _convert(H, f, Aeq, beq, lb, ub)
    results = qp(P, q, G, h, A, b)

    # Convert back to NumPy matrix
    # and return solution
    xstar = results['x']
    return np.matrix(xstar)

def _convert(H, f, Aeq, beq, lb, ub):                                                                                  
    """
    Convert everything to                                                                                              
    cvxopt-style matrices                                                                                              
    """ 
    P = cvxmat(H)                                                                                                      
    q = cvxmat(f)
    if Aeq is None:                                                                                                    
        A = None                                                                                                       
    else: 
        A = cvxmat(Aeq)                                                                                                
    if beq is None:                                                                                                    
        b = None                                                                                                       
    else: 
        b = cvxmat(beq)                                                                                                
    
    n = lb.size
    G = sparse([-speye(n), speye(n)])                                                                                  
    h = cvxmat(np.vstack([-lb, ub]))                                                                                      
    return P, q, G, h, A, b 

def speye(n):
    """Create a sparse identity matrix"""
    r = range(n)
    return spmatrix(1.0, r, r)