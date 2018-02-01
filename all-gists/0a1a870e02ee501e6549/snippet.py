# plot weight of oit

import matplotlib.pyplot as plt
import numpy as np

N = 1000
z = np.linspace(1, 500, N)


def clamp(a, amin, amax):
    return np.max([amin, np.min([a, amax])])


def equation7(z):
    zabs = np.abs(z)
    val = 10. / (1e-5 + np.power(zabs/5.0, 2.0) + np.power(zabs/200.0, 6.0))
    return clamp(val, 1e-2, 3e3)


def equation8(z):
    zabs = np.abs(z)
    val = 10. / (1e-5 + np.power(zabs/5.0, 3.0) + np.power(zabs/200.0, 6.0))
    return clamp(val, 1e-2, 3e3)


def equation9(z):
    val = 0.001/(1e-5 + np.power(np.abs(z)/200.0, 4.0))
    return clamp(val, 1e-2, 3e3)


zw = np.array([[equation7(zi), equation8(zi), equation9(zi)] for zi in z])

plt.loglog(zw)
plt.xlim([1, 1000])
