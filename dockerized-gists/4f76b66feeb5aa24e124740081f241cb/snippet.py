#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from cvxopt import solvers
from cvxopt import matrix

def toysvm():
    def to_matrix(a):
        return matrix(a, tc='d')    
    X = np.array([
        [0,2],
        [2,2],
        [2,0],
        [3,0]        
        ])
    y = np.array([-1,-1,1,1])
    Qd = np.array([
        [0,0,0,0],
        [0,8,-4,-6],
        [0,-4,4,6],
        [0,-6,6,9],
        ])
    Ad = np.array([
        [-1,-1,1,1],
        [1,1,-1,-1],
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]
        ])
    N = len(y)
    P = to_matrix(Qd)
    q = to_matrix(-(np.ones((N))))
    G = to_matrix(-Ad)
    h = to_matrix(np.array(np.zeros(N+2)))
    sol = solvers.qp(P,q,G,h)
    print(sol['x'])

if __name__ == "__main__":
        toysvm()
