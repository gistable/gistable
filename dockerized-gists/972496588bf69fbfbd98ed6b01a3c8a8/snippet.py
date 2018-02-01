class BayesianModel(object):
    samples = 2000
    def __init__(self, cache_model=True):
        self.cached_model = None
        self.cached_start = None
        self.cached_sampler = None
        self.shared_vars = {}

    def cache_model(self, **inputs):
        self.shared_vars = self._create_shared_vars(**inputs)
        self.cached_model = self.create_model(**self.shared_vars)

    def create_model(self, **inputs):
        raise NotImplementedError('This method has to be overwritten.')

    def _create_shared_vars(self, **inputs):
        shared_vars = {}
        for name, data in inputs.items():
            shared_vars[name] = shared(np.asarray(data), name=name)
        return shared_vars

    def run(self, reinit=True, **inputs):
        if self.cached_model is None:
            self.cache_model(**inputs)

        for name, data in inputs.items():
            self.shared_vars[name].set_value(data)

        trace = self._inference(reinit=reinit)
        return trace

    def _inference(self, reinit=True):
        with self.cached_model:
            if reinit or (self.cached_start is None) or (self.cached_sampler is None):
                self.cached_start = pm.find_MAP(fmin=sp.optimize.fmin_powell)
                self.cached_sampler = pm.NUTS(scaling=self.cached_start)
            
            trace = pm.sample(self.samples, self.cached_sampler, start=self.cached_start)

        return trace
    
class BEST(BayesianModel):
    """Bayesian Estimation Supersedes the T-Test
    This model replicates the example used in:
    Kruschke, John. (2012) Bayesian estimation supersedes the t
    test. Journal of Experimental Psychology: General.
    The original pymc2 implementation was written by Andrew Straw and
    can be found here: https://github.com/strawlab/best
    Ported to PyMC3 by Thomas Wiecki (c) 2015.
    """
    def create_model(self, y1=None, y2=None):
        y = pm.concatenate((y1, y2))

        mu_m = T.mean(y)
        mu_p = 0.000001 * 1 / y.std()**2

        sigma_low = y.std()/1000
        sigma_high = y.std()*1000

        with pm.Model() as model:
            group1_mean = pm.Normal('group1_mean', mu=mu_m, tau=mu_p,
                                    testval=y1.mean())
            group2_mean = pm.Normal('group2_mean', mu=mu_m, tau=mu_p,
                                    testval=y2.mean())
            group1_std = pm.Uniform('group1_std', lower=sigma_low,
                                    upper=sigma_high, testval=y1.std())
            group2_std = pm.Uniform('group2_std', lower=sigma_low,
                                    upper=sigma_high, testval=y2.std())
            nu = pm.Exponential('nu_minus_two', 1 / 29., testval=4.) + 2.
    
            returns_group1 = pm.StudentT('group1', nu=nu, mu=group1_mean,
                                  lam=group1_std**-2, observed=y1)
            returns_group2 = pm.StudentT('group2', nu=nu, mu=group2_mean,
                                  lam=group2_std**-2, observed=y2)

            diff_of_means = pm.Deterministic('difference of means',
                                             group2_mean - group1_mean)
            pm.Deterministic('difference of stds',
                             group2_std - group1_std)
            pm.Deterministic('effect size', diff_of_means /
                             pm.sqrt((group1_std**2 +
                                      group2_std**2) / 2))

            pm.Deterministic('group1_annual_volatility',
                             returns_group1.distribution.variance**.5 *
                             np.sqrt(252))
            pm.Deterministic('group2_annual_volatility',
                             returns_group2.distribution.variance**.5 *
                             np.sqrt(252))

            pm.Deterministic('group1_sharpe', returns_group1.distribution.mean /
                             returns_group1.distribution.variance**.5 *
                             np.sqrt(252))
            pm.Deterministic('group2_sharpe', returns_group2.distribution.mean /
                             returns_group2.distribution.variance**.5 *
                             np.sqrt(252))

        return model

    def analyze(self, trace=None, burn=200, ax1=None, ax2=None, ax3=None):
        trace = trace[burn:]

        if ax1 is None:
            fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(16, 4))

        sns.distplot(trace['group1_mean'], ax=ax1, label='backtest')
        sns.distplot(trace['group2_mean'], ax=ax1, label='forward')
        ax1.legend(loc=0)
        # sns.distplot(trace['difference of means'], ax=ax2)
        # ax2.axvline(0, linestyle='-', color='k')
        # ax2.axvline(
        #     stats.scoreatpercentile(trace['difference of means'], 2.5),
        #     linestyle='--', color='b', label='2.5 and 97.5 percentiles')
        # ax2.axvline(
        #     stats.scoreatpercentile(trace['difference of means'], 97.5),
        #     linestyle='--', color='b')
        # ax2.legend(loc=0)

        sns.distplot(trace['effect size'], ax=ax2)
        ax2.axvline(0, linestyle='-', color='k')
        ax2.axvline(
            stats.scoreatpercentile(trace['effect size'], 2.5),
            linestyle='--', color='b')
        ax2.axvline(
            stats.scoreatpercentile(trace['effect size'], 97.5),
            linestyle='--', color='b')
        ax1.set_xlabel('mean')
        ax2.set_xlabel('difference of means')
        ax2.set_xlabel('effect size')


best = BEST()
