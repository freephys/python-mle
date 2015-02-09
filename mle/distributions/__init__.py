
import numpy as np
import theano.tensor as T
from numpy import inf, array, ndarray

from mle.model import Model

__all__=['Uniform', 'Normal', 'Mix2']

def alltrue(vals):
    ret = 1
    for c in vals:
        ret = ret * (1 * c)
    return ret

def bound(logp, *conditions):
    return T.switch(alltrue(conditions), logp, -np.inf)

class Uniform(Model):
    def __init__(self, x, lower, upper, *args, **kwargs):
        self._logp = T.log(T.switch(T.gt(x, upper), 0, T.switch(T.lt(x, lower), 0, 1/(upper - lower))))
        self._cdf = T.switch(T.gt(x, up), 1, T.switch(T.lt(x, low), 0, (x - low)/(up - low)))
        super(Uniform, self).__init__(*args, **kwargs)
        self._add_expr('x', x)
        self._add_expr('lower', lower)
        self._add_expr('upper', upper)

class Normal(Model):
    def __init__(self, x, mu, sigma, *args, **kwargs):
        self._logp = bound(-(x - mu)**2 / (2 * sigma**2) + T.log(1 / T.sqrt(sigma**2 * 2 * np.pi)), sigma > 0)
        self._cdf = 0.5 * (1 + T.erf((x - mu)/(sigma*T.sqrt(2))))
        super(Normal, self).__init__(*args, **kwargs)
        self._add_expr('x', x)
        self._add_expr('mu', mu)
        self._add_expr('sigma', sigma)

class Mix2(Model):
    def __init__(self, theta, dist1, dist2, *args, **kwargs):
        self._logp = bound(T.log(theta * T.exp(dist1._logp) + (1 - theta) * T.exp(dist2._logp)), theta > 0, theta < 1)
        self._cdf = lambda: self.theta * self.dist1._cdf + (1-self.theta) * self.dist2._cdf
        super(Mix2, self).__init__(*args, **kwargs)
        self._add_expr('theta', theta)
        self._add_submodel('dist1', dist1)
        self._add_submodel('dist2', dist2)
