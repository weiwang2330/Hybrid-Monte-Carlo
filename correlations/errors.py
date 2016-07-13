import numpy as np

from hmc import checks
from acorr import acorr as getAcorr

__doc__ = """This code is based on ``Monte Carlo errors with less errors''
 - by Ulli Wolff, hep-lat/0306017

The aim is to make the routine more readable and simplified with python
"""

def intAcorr(acorrn, w):
    """Calculates the integrated autocorellations by integrating
    up to a window length, w across the autocorrelation function
    
    Required Inputs
        acorrn :: np.ndarray :: normalised autocorrelation function
        w      :: int  :: the window to integrate up to
    
    Returns
        itau      :: float :: integrated autocorrelation function
        itau_diff :: float :: errors in itau
        itau_aav  :: np.ndarray :: itau at each window length
    """
    itau_aav  = np.cumsum(acorrn) - .5              # Eq. (41)
    itau      = itau_aav[w]
    itau_diff = itau*2*np.sqrt((w - itau + .5)/n)
    return itau, itau_diff, itau_aav

def gW(t, g_int, s_tau, n):
    """Calculates g_W as in Eq. (52)
    
    Required Inputs
        t :: int :: MCMC sample time
        g_int :: float :: somewhere around Eq.50?
        s_tau :: float :: S(t) in the equation
        n     :: int   :: f_ret.size
    """
    # np.nan handles the divisino by 0 fine (tested)
    tau_w = s_tau / np.log(1. + 1./g_int.clip(0))
    g_w = np.exp(-t/tau_w) - tau_w/np.sqrt(t*n)
    return g_w

def autoWindow(acorrn, s_tau, n):
    """Automatic windowing procedure as 
    described in Section 3.3 in the paper
    
    Required Inputs
        acorr :: np.ndarray :: normalised autocorellations
        s_tau :: float      :: guess for the ratio S of tau/itau
        n     :: int        :: f_ret.size
    """
    g_int = np.cumsum(acorrn[:t_max]) # cumulative sum
    for t,v in enumerate(g_int):
        # look for a sign switch in g_w
        # optimal w occurs when sign changes
        if gW(t, v, s_tau, n) < 0: 
            w_best = t
            break
    
    t_max = min(t_max, 2*w_best)
    check.tryAssertNotEqual(flag, False,
        msg = 'Windowing condition failed up to W = {}'.format(t_max))
    
    return w_best, t_max
    
def uWerr(f_ret, s_tau=1.5):
    """autocorrelation-analysis of MC time-series following the Gamma-method
    This (simplified) implementation assumes f_ret have been acted upon by an operator
    and just completes basic calculations
    
    **Currently only supports ONE observable of length sample.shape[0]**
    
    Required Inputs
        f_ret   :: np.ndarray :: the return of a function action upon all f_ret
        s_tau   :: float>0 :: guess for the ratio S of tau/tauint [D=1.5]
    
    Optional Inputs
        name     :: str/None :: observable titles for plots. None: no plots.
        n_rep    :: np.ndarray :: list of int: len of each data for replica of len n_rep
        quantity :: int :: shouldn't be used
    
    Notation notes:
        x_av0 is an average of x over the 0th dim - \bar{x}^r in the paper
        x_aav is the average over all dims        - \bbar{x} in the paper
        v_err is the error in v                   - \sigma_F in the paper
        v_eerr is the error of the error          - given by Eq. 40 : no symbol in paper
    
    s_tau or Stau in the original code doesn't work for the 0 case so I removed it.
    see https://github.com/flipdazed/Hybrid-Monte-Carlo/issues/34#issuecomment-232472657
    for info.
    """
    check.tryAssertNotEqual(s_tau, 0,
        msg = 's_tau cannot be zero, see:\n' \
        + 'https://github.com/flipdazed/Hybrid-Monte-Carlo' \
        + '/issues/34#issuecomment-232472657')
    
    # legacy: n_rep is set up as the number of entries in the data if reps = None
    n = float(f_ret.size)
    
    # a_av0 is equal to a_aav beacuse we have no replicas here
    # note that f_aav == a_aav because R=1
    f_aav = a_aav = np.average(f_ret)   # get the mean of the function outputs
    diffs = f_ret - a_aav               # get fluctuations around mean
    
    norm = (diffs**2).mean() # values for w = 0
    check.tryAssertNotEqual(norm, 0,
        msg = 'Normalisation cannot be zero: No fluctuations.' \
        + '\nNormalisation: {}'.format(norm))
    
    t_max = get_t*int(n)/2 # int div deliberate and bool mult
    
    # just makes it more readable - this fills static parameters and only varies t
    # don't normalise until bias corrected
    fn = lambda t: getAcorr(samples=f_ret, mean=f_aav, separation=t, norm=None)
    
    # this maps the function to every item in the range, returns as list
    # and appends to the existing entry of [norm]
    acorr  = np.asarray([norm] + map(fn, range(1, t_max)))
    
    # The automatic windowing proceedure
    w_best, t_max = autoWindow(acorrn=acorr/norm, s_tau=s_tau, n=n)
    
    # this starting point is defined as Eq. 35 in the paper
    c_aav = norm + 2.*acorr[1:w_best].sum()
    check.tryAssertLt(flag, g_sum,
        msg = 'Estimated error^2 as sum(gamma) < 0...\n sum = {}'.format(g_sum))
    
    acorr    += c_aav/n     # correct bias from Eq. (31) as decribed in Eq. (32/49)
    c_aav     = norm + 2*acorr[1:w_best].sum()  # refine estimate with  Eq. (35)
    acorrn    = acorr/norm                      # normalise autocorr fn.
    
    itau, itau_diff, itau_aav = intAcorr(acorrn=acorrn, w=w_best)
    f_diff  = np.sqrt(c_aav/n)                  # error of f from       Eq. (44)
    f_ddiff = f_diff*sqrt((w_best + itau + .5)/n)      # error on error of f   Eq. ()
    
    return f_aav, f_diff, f_ddiff, itau, itau_diff, itau_aav
