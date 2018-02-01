"""
C-alpha test for rare variants. Copied from AssotesteR
Only reports the permutation p-value, not the asymptotic

This also wraps all of the functions in R's AssotesteR using
rpy2. Any function available in AssotesteR, e.g. CALPHA is 
availailable here has r_calpha().
The args are always

casecon: a list of 0's, 1's indicating case/control status
genotype: a numpy array with shape len(casecon), n_snps.

the return value is a dictionary with keys of: stat, perm_p,
asym_p, function.

# TODO: http://www.ncbi.nlm.nih.gov/pubmed/21769936
"""
import numpy as np

import rpy2.robjects.numpy2ri as nri
from rpy2 import robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.functions import SignatureTranslatedFunction
AssotesteR = importr("AssotesteR")

class rassotest(object):
    def __init__(self, func_name):
        self.function_name = func_name
        self.fn = getattr(AssotesteR, func_name)

    def __call__(self, casecon, genotype, **kwargs):
        casecon = robjects.IntVector(casecon)
        genotype = nri.numpy2ri(genotype)
        res = self.fn(robjects.IntVector(casecon), nri.numpy2ri(genotype), **kwargs)
        res = dict(res.iteritems())
        # convert from rpy2 stuffs to python dict.
        skey = [k for k in res if k.endswith('.stat')][0]
        perm_p = res['perm.pval'][0]
        asym_p = res.get('asym.pval', [None])[0]
        return dict(stat=res[skey][0], perm_p=perm_p, asym_p=asym_p,
                   function=self.function_name)


# wrapper for SKAT.
class PySKAT(object):
    """
    covs is a list of covariates. each list in covs should be the same
    length as cc
    """
    def __init__(self, cc, covs=None):
        if hasattr(covs, "__iter__") and not hasattr(covs[0], "__iter__"):
            covs = [covs]
        elif covs is None:
            covs = []

        formula = "cc ~ 1 "
        cov_string = " + ".join("V%i" % i for i, cov in enumerate(covs))
        if covs != []:
            formula += " + " + cov_string
        fml = robjects.Formula(formula)
        fml.environment['cc'] = robjects.IntVector(cc)
        for i, cov in enumerate(covs):
            assert len(cov) == len(cc)
            fml.environment["V%i" % i] = robjects.FloatVector(cov)
        fml.environment['cc'] = robjects.IntVector(cc)
        self.obj = SKAT.SKAT_Null_Model(fml)
        self.formula = formula

    def __call__(self, genotype):
        _ = sys.stdout
        sys.stdout = sys.stderr
        sk_res = SKAT.SKAT(nri.numpy2ri(genotype.T), self.obj, method="optimal")
        sys.stdout = _

        py_res = dict(sk_res.iteritems())
        skat_pval = py_res['p.value'][0]
        params = dict(py_res['param'].iteritems())
        rho_est = params['rho_est'][0]
        return skat_pval, rho_est




# these 2 lines are unnessecary.
# the below loop imports and wraps all of the R functions
r_calpha = rassotest("CALPHA")
r_cmat = rassotest("CMAT")

# import and wrap all the functions in AssotesteR
for name in dir(AssotesteR):
    if isinstance(getattr(AssotesteR, name), SignatureTranslatedFunction):
        fname = "r_" + name.lower()
        globals()[fname] = rassotest(name)


# python version of calpha
def _calpha(casecon, genotype):
    nCase = casecon.sum()
    nControl = len(casecon) - nCase
    pCase = nCase / float(nControl + nCase)

    n = (genotype > 0).sum(0)
    g = (genotype[casecon == 1,] > 0).sum(0)

    Talpha = ((g - n * pCase)**2 - (n * pCase * (1 - pCase))).sum()
    return Talpha

def calpha(casecon, genotype, n_perm=10000):
    casecon = np.asarray(casecon)

    calpha_stat = _calpha(casecon, genotype)

    perm_stats = []
    rand_cc = casecon.copy()
    for i in xrange(n_perm):
        np.random.shuffle(rand_cc)
        perm_stats.append(_calpha(rand_cc, genotype))

    perm_stats = np.array(perm_stats) ** 2
    return calpha_stat, (1 + (perm_stats > (calpha_stat ** 2)).sum()) / float(n_perm + 1)

def _cmat(casecon, g):

    nCase = casecon.sum()
    nCtrl = len(casecon) - nCase

    mCase = g[casecon == 1,:].sum()
    mCtrl = g[casecon == 0,:].sum()

    iCase = (2 - g[casecon == 1,:]).sum()
    iCtrl = (2 - g[casecon == 0,:]).sum()

    cm1 = len(casecon) / (2. * nCase * nCtrl * g.shape[1])
    cm2 = ((mCase * iCtrl - mCtrl * iCase)**2) / \
            float((mCase + mCtrl) * (iCase + iCtrl))
    return cm1 * cm2

def cmat(casecon, genotype, n_perm=100, rare_cutoff="auto"):
    if rare_cutoff == "auto":
        # cutoff from SKAT CommonRare
        rare_cutoff = 1 / np.sqrt(2 * len(casecon))
    casecon = np.asarray(casecon)

    # just do this once since we only shuffle case/control status
    mafs = genotype.mean(0) / 2
    if any(mafs < rare_cutoff):
        genotype = genotype[:, mafs < rare_cutoff]
    else:
        return (np.nan, np.nan)
    cmat_stat = _cmat(casecon, genotype)

    perm_stats = []
    rand_cc = casecon.copy()
    for i in xrange(n_perm):
        np.random.shuffle(rand_cc)
        perm_stats.append(_cmat(rand_cc, genotype))

    perm_stats = np.array(perm_stats)
    return cmat_stat, (1. + (perm_stats > cmat_stat).sum()) / float(1 + n_perm)


if __name__ == "__main__":
    casecon = [0] * 100 + [1] * 100
    genotype = np.random.randint(0, 1, (len(casecon), 20))
    #genotype += np.random.randint(0, 1, (len(casecon), 20))
    genotype[120:130,1:5] = 1
    print cmat(casecon, genotype, rare_cutoff=0.05)

    print(r_cmat(casecon, genotype, perm=100, maf=1/np.sqrt(2*len(casecon))))
    #print(r_cmc(casecon, genotype, perm=400))
    #print(r_asum(casecon, genotype, perm=400))
    #print(r_bst(casecon, genotype, perm=400))
    #print(r_wss(casecon, genotype, perm=400))
    #print(r_assuw(casecon, genotype, perm=400))
    #print(r_wst(casecon, genotype, perm=400))
    print "R calpha:"
    print(r_calpha(casecon, genotype, perm=400))
    print "numpy calpha:"
    print calpha(casecon, genotype)
    print "numpy cmat:"
