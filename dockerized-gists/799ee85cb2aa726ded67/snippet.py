"""
Note that this Gist uses functions made available in another Gist -
https://gist.github.com/StuartGordonReid/67a1ec4fbc8a84c0e856
"""


def treynor_ratio(er, returns, market, rf):
    return (er - rf) / beta(returns, market)
 
 
def sharpe_ratio(er, returns, rf):
    return (er - rf) / vol(returns)
 
 
def information_ratio(returns, benchmark):
    diff = returns - benchmark
    return numpy.mean(diff) / vol(diff)
 
 
def modigliani_ratio(er, returns, benchmark, rf):
    np_rf = numpy.empty(len(returns))
    np_rf.fill(rf)
    rdiff = returns - np_rf
    bdiff = benchmark - np_rf
    return (er - rf) * (vol(rdiff) / vol(bdiff)) + rf