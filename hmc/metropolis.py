import numpy as np

class Accept_Reject(object):
    """Contains accept-reject routines
    
    Required Inputs
        rng :: np.random.RandomState :: random number generator
    
    Optional Inputs
        store_acceptance :: bool :: optionally store the acceptance rates
        accept_all :: Bool :: function always returns True
    """
    def __init__(self, rng, store_acceptance = False, accept_all = False):
        self.rng = rng
        self.store_acceptance = store_acceptance
        self.accept_all = accept_all
        
        # both will only take values if store_acceptance == True
        self.accept_rates = []   # list of acceptance rates
        self.accept_rejects = [] # list of acceptance or rejections
        self.delta_hs = []       # list of delta_hs
        self.h_olds = []
        self.h_news = []
        pass
    
    def metropolisHastings(self, h_old, h_new):
        """A M-H accept/reject test as per
        Duane, Kennedy, Pendleton (1987)
        and also used by Neal (2003)
        
        The following, 
            min(1., np.exp(-delta_h)) - self.rng.uniform() >= 0.
            (np.exp(-delta_h) - self.rng.uniform()) >= 0
        
        are equivalent to the original step:
            self.rng.uniform() < min(1., np.exp(-delta_h))
        
        The min() function need not be evaluated as both
        the resultant 1. a huge +ve number will both result
        in acceptance.
        >= is also introduced for OCD reasons.
        
        Required Inputs
            h_old :: float :: old hamiltonian
            h_new :: float :: new hamiltonian
        
        Return :: bool
            True    :: acceptance
            False   :: rejection
        """
        delta_h = h_new - h_old
        
        if self.accept_all:
            accept_reject = True
        else:
            # (self.rng.uniform() < min(1., np.exp(-delta_h))) # Neal / DKP original
            accept_reject = (np.exp(-delta_h) - self.rng.uniform()) >= 0 # faster
        
        # stores useful values for analysis during runtime
        if self.store_acceptance:
            self.accept_rates.append(min(1, np.exp(-delta_h)))
            self.accept_rejects.append(accept_reject)
            self.delta_hs.append(delta_h)
            self.h_olds.append(h_old)
            self.h_news.append(h_new)
            
        return accept_reject

