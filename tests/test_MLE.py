from pymuse.analyse import MaximumLikelihood

import numpy as np
from scipy.special import factorial

def gaussian(x,mu,sig):
    return 1/np.sqrt(2*np.pi*sig**2) * np.exp(-(x-mu)**2/(2*sig**2))

def test_gaussian():
    n_data = 500
    mu, sig = 3.141, 2.71
    data = np.random.normal(mu,sig,n_data)

    fit = MaximumLikelihood(gaussian,data)
    mu_f, sig_f = fit([1.2*mu,0.8*sig])

    assert (mu_f-mu)/mu < 0.1 
    assert (sig_f-sig)/sig < 0.1

def poission(k,lam):
    return lam**k * np.exp(-lam) / factorial(k)

def test_poission():
    n_data = 500
    lam = 4
    data = np.random.poisson(lam,n_data)

    fit = MaximumLikelihood(poission,data)
    lam_f = fit([1.4*lam])

    assert (lam_f-lam)/lam < 0.1 