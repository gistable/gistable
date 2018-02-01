{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<img src=\"http://hilpisch.com/tpq_logo.png\" width=\"350px\">"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Finance with Python"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "This is a class about _Python_ for **Finance**.\n",
    "\n",
    "$$\n",
    "\\frac{dS_t}{S_t} = r dt + \\sigma dZ_t\n",
    "$$\n",
    "\n",
    "This is Latex $S_t$."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "7"
      ]
     },
     "execution_count": 1,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "3 + 4"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "12"
      ]
     },
     "execution_count": 2,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "3 * 4"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Financial Market"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "import numpy as np"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "B0 = 10"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "S0 = 10"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "B = np.array([11, 11])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "S = np.array([20, 5])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([11, 11])"
      ]
     },
     "execution_count": 8,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "B"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "dtype('int64')"
      ]
     },
     "execution_count": 9,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "B.dtype"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([22, 22])"
      ]
     },
     "execution_count": 10,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "B * 2"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "[11, 11, 11, 11]"
      ]
     },
     "execution_count": 11,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "[11, 11] * 2"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "22"
      ]
     },
     "execution_count": 12,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "B.sum()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "12.5"
      ]
     },
     "execution_count": 13,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "S.mean()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "C = np.maximum(S - 15, 0)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([5, 0])"
      ]
     },
     "execution_count": 15,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "C"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "5"
      ]
     },
     "execution_count": 16,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "max(C)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "def ret(x0, x):\n",
    "    return x.mean() / x0 - 1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0.10000000000000009"
      ]
     },
     "execution_count": 18,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "ret(B0, B)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0.25"
      ]
     },
     "execution_count": 19,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "ret(S0, S)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "C0 = C.mean() / (1 + 0.1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "2.2727272727272725"
      ]
     },
     "execution_count": 21,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "C0"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "i = 0.1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([ 23.5,  10. ])"
      ]
     },
     "execution_count": 23,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "0.5 * B + 0.9 * S"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "M0 = np.array([B0, S0])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([10, 10])"
      ]
     },
     "execution_count": 25,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "M0"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 26,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "M = np.array([B, S]).T"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[11, 20],\n",
       "       [11,  5]])"
      ]
     },
     "execution_count": 27,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "M"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "phi = np.linalg.solve(M, C)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([-0.15151515,  0.33333333])"
      ]
     },
     "execution_count": 29,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "phi"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([ 5.,  0.])"
      ]
     },
     "execution_count": 30,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.dot(M, phi).round(2)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "C0r = np.dot(M0, phi)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "1.8181818181818181"
      ]
     },
     "execution_count": 32,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "C0r"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "2.2727272727272725"
      ]
     },
     "execution_count": 33,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "C0"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "C0 = C.mean() / (1 + 0.25) "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "2.0"
      ]
     },
     "execution_count": 35,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "C0"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 36,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0.375"
      ]
     },
     "execution_count": 36,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "ret(C0r, C)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 37,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "1.8181818181818181"
      ]
     },
     "execution_count": 37,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "C.mean() / (1 + 0.375)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Deriving the Martingale Measure"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 38,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "from scipy.optimize import minimize"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 39,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "bnds = ((0, 1), (0, 1))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 40,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "def E(Q):\n",
    "    return np.dot(S, Q) - S0 * (1 + i)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 41,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "def E(Q):\n",
    "    return (np.dot(S, Q) - S0 * (1 + i)) ** 2"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 42,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "Q = np.array([0.45, 0.55])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 43,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0.5625"
      ]
     },
     "execution_count": 43,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "E(Q)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 44,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "cons = (\n",
    "    {'type': 'eq', 'fun': lambda Q: Q.sum() - 1} #,\n",
    "    # {'type': 'eq', 'fun': lambda Q: E(Q)}\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 45,
   "metadata": {},
   "outputs": [],
   "source": [
    "res = minimize(E, (0.5, 0.5), bounds=bnds,\n",
    "               constraints=cons)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 46,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "     fun: 1.2556709968339189e-14\n",
       "     jac: array([  1.47819541e-06,  -7.48038236e-07])\n",
       " message: 'Optimization terminated successfully.'\n",
       "    nfev: 9\n",
       "     nit: 2\n",
       "    njev: 2\n",
       "  status: 0\n",
       " success: True\n",
       "       x: array([ 0.39999999,  0.60000001])"
      ]
     },
     "execution_count": 46,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "res"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 47,
   "metadata": {},
   "outputs": [],
   "source": [
    "Q = res['x']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 48,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "1.2556709968339189e-14"
      ]
     },
     "execution_count": 48,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "E(Q)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 49,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "11.0"
      ]
     },
     "execution_count": 49,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "S0 * 1.1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 50,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "10.999999887943273"
      ]
     },
     "execution_count": 50,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.dot(S, Q)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 51,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "C0m = np.dot(C, Q) / (1 + i)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 52,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "1.8181817842252341"
      ]
     },
     "execution_count": 52,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "C0m"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 53,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "1.8181818181818181"
      ]
     },
     "execution_count": 53,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "C0r"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Incomplete Market"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 54,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "B = np.array([11, 11, 11])\n",
    "S = np.array([20, 10, 5])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 55,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([10, 10])"
      ]
     },
     "execution_count": 55,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "M0"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 56,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "M = np.array((B, S)).T"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 57,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[11, 20],\n",
       "       [11, 10],\n",
       "       [11,  5]])"
      ]
     },
     "execution_count": 57,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "M"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 58,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "C = np.maximum(S - 15, 0)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 59,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([5, 0, 0])"
      ]
     },
     "execution_count": 59,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "C"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 60,
   "metadata": {},
   "outputs": [],
   "source": [
    "lsq = np.linalg.lstsq(M, C)[0]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 61,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([ 4.64285714,  1.07142857, -0.71428571])"
      ]
     },
     "execution_count": 61,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.dot(M, lsq)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 62,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "1.2987012987012982"
      ]
     },
     "execution_count": 62,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.dot(M0, lsq)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 63,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([-0.35714286,  1.07142857, -0.71428571])"
      ]
     },
     "execution_count": 63,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.dot(M, lsq) - C"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 64,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([ True,  True,  True], dtype=bool)"
      ]
     },
     "execution_count": 64,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "5 / 11 * B >= C"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 65,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "4.545454545454545"
      ]
     },
     "execution_count": 65,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "5 / 11 * B0"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 66,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([5, 0, 0])"
      ]
     },
     "execution_count": 66,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "C"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 67,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "def costs(phi):\n",
    "    return np.dot(M0, phi)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 68,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "cons = ({'type': 'ineq', 'fun': lambda phi: np.dot(M, phi) - C})"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 69,
   "metadata": {},
   "outputs": [],
   "source": [
    "res = minimize(costs, (0.5, 0.5), constraints=cons)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 70,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "     fun: 1.8181818181822074\n",
       "     jac: array([ 10.,  10.])\n",
       " message: 'Optimization terminated successfully.'\n",
       "    nfev: 8\n",
       "     nit: 2\n",
       "    njev: 2\n",
       "  status: 0\n",
       " success: True\n",
       "       x: array([-0.15151515,  0.33333333])"
      ]
     },
     "execution_count": 70,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "res"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 71,
   "metadata": {},
   "outputs": [],
   "source": [
    "phi = res['x']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 72,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([ 0.   ,  1.667,  0.   ])"
      ]
     },
     "execution_count": 72,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.dot(M, phi).round(3) - C"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Mean Variance Portfolio Theory"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 73,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "# alt payoff\n",
    "B = np.array((5, 15, 11))\n",
    "M = np.array((B, S)).T"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 74,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[ 5, 20],\n",
       "       [15, 10],\n",
       "       [11,  5]])"
      ]
     },
     "execution_count": 74,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "M"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 75,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([10, 10])"
      ]
     },
     "execution_count": 75,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "M0"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 76,
   "metadata": {},
   "outputs": [],
   "source": [
    "R = M / M0 - 1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 77,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[-0.5,  1. ],\n",
       "       [ 0.5,  0. ],\n",
       "       [ 0.1, -0.5]])"
      ]
     },
     "execution_count": 77,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "R"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 78,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0.10000000000000002"
      ]
     },
     "execution_count": 78,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "R.mean()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 79,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([ 0.03333333,  0.16666667])"
      ]
     },
     "execution_count": 79,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "R.mean(axis=0)\n",
    "# mean return per financial asset for equal probability"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 80,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([ 0.25,  0.25, -0.2 ])"
      ]
     },
     "execution_count": 80,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "R.mean(axis=1)\n",
    "# mean return per state for equal weight portfolio"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 81,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([ 0.41096093,  0.62360956])"
      ]
     },
     "execution_count": 81,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "R.std(axis=0)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 82,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "def mu(phi):\n",
    "    return np.dot(R.mean(axis=0), phi)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 83,
   "metadata": {},
   "outputs": [],
   "source": [
    "def vol(phi):\n",
    "    return np.dot(phi, np.dot(np.cov(R.T, ddof=0), phi)) ** 0.5"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 84,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "phi = (0.5, 0.5)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 85,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0.10000000000000001"
      ]
     },
     "execution_count": 85,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "mu(phi)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 86,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0.21213203435596423"
      ]
     },
     "execution_count": 86,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "vol(phi)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 87,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "phi = (0, 1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 88,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0.16666666666666666"
      ]
     },
     "execution_count": 88,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "mu(phi)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 89,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0.62360956446232352"
      ]
     },
     "execution_count": 89,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "vol(phi)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 90,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "phi = (1, 0)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 91,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0.033333333333333361"
      ]
     },
     "execution_count": 91,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "mu(phi)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 92,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "0.41096093353126506"
      ]
     },
     "execution_count": 92,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "vol(phi)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 93,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "s = np.linspace(-1, 2, 25)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 94,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([-1.   , -0.875, -0.75 , -0.625, -0.5  , -0.375, -0.25 , -0.125,\n",
       "        0.   ,  0.125,  0.25 ,  0.375,  0.5  ,  0.625,  0.75 ,  0.875,\n",
       "        1.   ,  1.125,  1.25 ,  1.375,  1.5  ,  1.625,  1.75 ,  1.875,  2.   ])"
      ]
     },
     "execution_count": 94,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "s"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 95,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "pos = [(1-s, s) for s in np.linspace(-1, 2, 50)]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 96,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "[(2.0, -1.0),\n",
       " (1.9387755102040818, -0.93877551020408168),\n",
       " (1.8775510204081631, -0.87755102040816324),\n",
       " (1.8163265306122449, -0.81632653061224492),\n",
       " (1.7551020408163265, -0.75510204081632648),\n",
       " (1.693877551020408, -0.69387755102040816),\n",
       " (1.6326530612244898, -0.63265306122448983),\n",
       " (1.5714285714285714, -0.5714285714285714),\n",
       " (1.510204081632653, -0.51020408163265307),\n",
       " (1.4489795918367347, -0.44897959183673475)]"
      ]
     },
     "execution_count": 96,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "pos[:10]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 97,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "mv = np.array([(vol(phi), mu(phi)) for phi in pos])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 98,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([[ 1.34907376, -0.1       ],\n",
       "       [ 1.29040285, -0.09183673],\n",
       "       [ 1.23178439, -0.08367347],\n",
       "       [ 1.17322624, -0.0755102 ],\n",
       "       [ 1.11473789, -0.06734694]])"
      ]
     },
     "execution_count": 98,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "mv[:5]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 99,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "from pylab import plt\n",
    "%matplotlib inline"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 100,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "plt.style.use('ggplot')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 101,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "[<matplotlib.lines.Line2D at 0x119278400>]"
      ]
     },
     "execution_count": 101,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "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\ndsRWXgAAAABJRU5ErkJggg==\n",
      "text/plain": [
       "<matplotlib.figure.Figure at 0x1191d9588>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "plt.plot(mv[:, 0], mv[:, 1], 'ro')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<img src=\"http://hilpisch.com/tpq_logo.png\" width=\"350px\">"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.1"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
